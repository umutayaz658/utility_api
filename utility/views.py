import tempfile
import pytz
from django.core.files.base import ContentFile
from fpdf import FPDF
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics
from django.http import FileResponse, Http404
from tools import settings
from .models import CustomURL, QuickNote, PDF
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
from PIL import Image
import os
from django.contrib.auth.models import User


# TOKEN VIEWS: STARTS


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

# TOKEN VIEWS: ENDS


# URL-SHORTENER VIEWS: STARTS.


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
def delete_url(request, short_url):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication credentials were not provided.'},
                        status=status.HTTP_401_UNAUTHORIZED)
    try:
        custom_url = CustomURL.objects.get(short_url=short_url)
    except CustomURL.DoesNotExist:
        return Response({'error': 'URL not found'}, status=status.HTTP_404_NOT_FOUND)

    is_deleted = request.data.get('is_deleted', None)

    if is_deleted is None:
        return Response({'error': '"is_deleted" field is required'}, status=status.HTTP_400_BAD_REQUEST)

    custom_url.is_deleted = is_deleted
    custom_url.save()

    return Response({'message': 'URL deleted successfully'}, status=status.HTTP_200_OK)


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
        if timezone.is_naive(new_validity_period):
            new_validity_period = timezone.make_aware(new_validity_period, timezone=pytz.UTC)
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


# URL-SHORTENER VIEWS: ENDS


# QUICK NOTE VIEWS: STARTS


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


class QuickNoteFileDownloadView(APIView):
    permission_classes = [AllowAny]
    ##test
    def get(self, request, note_id, *args, **kwargs):
        note = get_object_or_404(QuickNote, id=note_id)

        if note.file:
            file_path = note.file.path
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    response = HttpResponse(file.read(), content_type='application/octet-stream')
                    response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
                    return response
            else:
                raise Http404("File does not exist.")
        else:
            raise Http404("No file attached to this note.")


class UserAutocompleteView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    pagination_class = None

    def get_queryset(self):
        query = self.request.GET.get('send_to', '')
        if query:
            return User.objects.filter(username__istartswith=query)[:10]
        return User.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        user_list = [{'username': user.username} for user in queryset]
        return Response(user_list)

# QUICK NOTE VIEWS: ENDS


#QR CODE VIEWS: STARTS


class QRCodeAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data.get('data', '').strip()
        download_link = request.data.get('download_link', False)

        if not data:
            return Response({"error": "No data provided"}, status=400)

        qr_code_image, qr_code_filename = generate_qr_code(data)

        if download_link:
            qr_code_path = os.path.join("media/qr_codes", qr_code_filename)

            with open(qr_code_path, "wb") as qr_code_file:
                qr_code_file.write(qr_code_image)

            download_url = request.build_absolute_uri(f"/api/download-qr-code/{qr_code_filename}")
            return Response({"download_url": download_url})
        else:
            response = HttpResponse(qr_code_image, content_type='image/png')
            response['Content-Disposition'] = 'inline; filename="qrcode.png"'
            return response


def download_qr_code(request, filename):
    file_path = os.path.join("media/qr_codes", filename)

    if not os.path.exists(file_path):
        return HttpResponse(status=404)

    with open(file_path, "rb") as f:
        response = HttpResponse(f.read(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# QR CODE VIEWS: ENDS


# IMAGE TO PDF VIEWS: STARTS


class ImageToPDFView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        image_paths = request.data.getlist('image_paths')

        if not image_paths:
            return Response({'error': 'Select an image.'}, status=status.HTTP_400_BAD_REQUEST)

        images = []
        try:
            for path in image_paths:
                image = Image.open(path)
                images.append(image)
        except Exception as e:
            return Response({'error': f'Error: {e}'},
                            status=status.HTTP_400_BAD_REQUEST)

        pdf = FPDF()

        for image in images:
            image = image.convert('RGB')

            width, height = image.size
            width_mm = width * 0.264583
            height_mm = (height * 0.264583) * 210 / width_mm
            print(height_mm)
            page_height = 297
            y_position = (page_height - height_mm) / 2

            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_image:
                image.save(temp_image.name)
                pdf.add_page()
                pdf.image(temp_image.name, x=0, y=y_position, w=210, h=height_mm)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            pdf.output(temp_pdf.name)
            temp_pdf.seek(0)

            with open(temp_pdf.name, 'rb') as pdf_file:
                pdf_content = pdf_file.read()

            pdf_model = PDF()
            pdf_model.pdf.save("output.pdf", ContentFile(pdf_content))
            pdf_model.save()

        download_url = request.build_absolute_uri(f'/api/imagetopdf/download/{pdf_model.id}/')
        return Response({'download_url': download_url}, status=status.HTTP_201_CREATED)


class DownloadPDFView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk, *args, **kwargs):
        try:
            pdf = PDF.objects.get(pk=pk)
        except PDF.DoesNotExist:
            return Response({'error': 'PDF bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

        file_path = os.path.join(settings.MEDIA_ROOT, pdf.pdf.name)
        return FileResponse(open(file_path, 'rb'), as_attachment=True)


# IMAGE TO PDF VIEWS: ENDS
