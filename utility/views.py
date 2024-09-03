from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics
from .models import CustomURL, QuickNote
from .serializers import URLSerializer, URLDetailSerializer, QuickNoteSerializer, CustomTokenObtainPairSerializer, \
    CustomTokenRefreshSerializer
import random
import string
from rest_framework.decorators import api_view
import json
from django.utils import timezone
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse
from .utils import generate_qr_code


# TOKEN VİEWS: STARTS


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=205)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

# TOKEN VİEWS: ENDS


# URL-SHORTENER VİEWS: STARTS.


def generate_short_url():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


@api_view(['POST'])
def url_create_view(request):

    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication credentials were not provided.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    serializer = URLSerializer(data=request.data)

    if serializer.is_valid():

        short_url = generate_short_url()

        custom_url = CustomURL.objects.create(
            long_url=serializer.validated_data['long_url'],
            validity_period=serializer.validated_data['validity_period'],
            created_by=request.user,
            is_active=serializer.validated_data['is_active'],
            one_time_only=serializer.validated_data['one_time_only'],
            password=serializer.validated_data['password'],
            short_url=short_url
        )

        custom_url.save()

        return Response({'short_url': short_url}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class URLDetailView(generics.ListAPIView):
    serializer_class = URLDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomURL.objects.filter(created_by=self.request.user)


@api_view(['POST'])
def get_long_url(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication credentials were not provided.'},
                        status=status.HTTP_401_UNAUTHORIZED)
    try:
        data = request.data
        short_url = data.get('short_url')
        password = data.get('password')

        if not short_url:
            return Response({'error': 'short_url is required'}, status=400)

        try:
            custom_url = CustomURL.objects.get(short_url=short_url)
        except CustomURL.DoesNotExist:
            return Response({'error': 'URL not found'}, status=404)

        if not custom_url.is_active:
            return Response({'error': 'URL is expired or inactive'}, status=404)

        if custom_url.password:
            if not password:
                return Response({'error': 'Password is required'}, status=400)

            if not check_password(password, custom_url.password):
                return Response({'error': 'Invalid password'}, status=403)

        return Response({'long_url': custom_url.long_url})

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['PUT'])
def update_url_active_status(request, short_url):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication credentials were not provided.'},
                        status=status.HTTP_401_UNAUTHORIZED)
    try:
        custom_url = CustomURL.objects.get(short_url=short_url)
    except CustomURL.DoesNotExist:
        return Response({'error': 'URL not found'}, status=status.HTTP_404_NOT_FOUND)

    is_active = request.data.get('is_active', None)

    if is_active is None:
        return Response({'error': '"is_active" field is required'}, status=status.HTTP_400_BAD_REQUEST)

    custom_url.is_active = is_active
    custom_url.save()

    return Response({'message': 'URL status updated successfully'}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def update_validity_period(request, short_url):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication credentials were not provided.'},
                        status=status.HTTP_401_UNAUTHORIZED)
    custom_url = get_object_or_404(CustomURL, short_url=short_url)
    validity_period = request.data.get('validity_period', None)

    if validity_period is None:
        return Response({'error': '"validity_period" field is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        new_validity_period = timezone.datetime.fromisoformat(validity_period.replace('Z', '+00:00'))
    except ValueError:
        return Response({'error': 'Invalid date format for "validity_period"'}, status=status.HTTP_400_BAD_REQUEST)

    if new_validity_period < timezone.now():
        return Response({'error': 'Validity period cannot be in the past.'}, status=status.HTTP_400_BAD_REQUEST)

    custom_url.validity_period = new_validity_period
    custom_url.save()

    return Response({'message': 'Validity period updated successfully'}, status=status.HTTP_200_OK)


def redirect_to_long_url(request, short_url):
    custom_url = get_object_or_404(CustomURL, short_url=short_url)
    if custom_url.is_expired or not custom_url.is_active:
        return redirect('link_expired')
    if custom_url.password:
        if request.method == 'POST':
            entered_password = request.POST.get('password', '')
            if check_password(entered_password, custom_url.password):
                if custom_url.one_time_only:
                    custom_url.is_active = False
                    custom_url.save()
                return redirect(custom_url.long_url)
            else:
                return render(request, 'utility/security.html', context={"msg": "Invalid Password",
                                                                         "short_url": short_url})
        return render(request, 'utility/security.html', context={"msg": "", "short_url": short_url})
    if custom_url.one_time_only:
        custom_url.is_active = False
        custom_url.save()
    return redirect(custom_url.long_url)


def link_expired(request):
    return render(request, 'utility/expired.html')


# URL-SHORTENER VİEWS: ENDS


# QUICK NOTE VİEWS: STARTS


class QuickNoteCreateView(generics.CreateAPIView):
    serializer_class = QuickNoteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class UserSentNotesView(generics.ListAPIView):
    serializer_class = QuickNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuickNote.objects.filter(created_by=self.request.user)


class UserReceivedNotesView(generics.ListAPIView):
    serializer_class = QuickNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuickNote.objects.filter(send_to=self.request.user)

# QUICK NOTE VİEWS: ENDS


#QR CODE VİEWS: STARTS


class QRCodeAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data.get('data', '')
        if not data:
            return Response({"error": "No data provided"}, status=400)

        qr_code_image = generate_qr_code(data)

        response = HttpResponse(qr_code_image, content_type='image/png')
        response['Content-Disposition'] = 'inline; filename="qrcode.png"'
        return response


#QR CODE VİEWS: ENDS
