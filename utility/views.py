import hashlib

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics
from .models import CustomURL
from .serializers import URLSerializer
import random
import string


# URL-SHORTENER VİEWS: STARTS.


def generate_short_url():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


class URLListCreateView(generics.ListCreateAPIView):
    queryset = CustomURL.objects.all()
    serializer_class = URLSerializer

    def perform_create(self, serializer):
        short_url = generate_short_url()
        while CustomURL.objects.filter(short_url=short_url).exists():
            short_url = generate_short_url()
        serializer.save(short_url=short_url, created_at=timezone.now())


class URLDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomURL.objects.all()
    serializer_class = URLSerializer


class GetLongURLView(APIView):
    def get(self, request):
        short_url = request.query_params.get('short_url')
        password = request.query_params.get('password')

        if not short_url:
            return Response({"error": "short_url parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # URL'yi short_url ile bul
            custom_url = CustomURL.objects.get(short_url=short_url)
        except CustomURL.DoesNotExist:
            return Response({"error": "URL with the given short_url does not exist."},
                                status=status.HTTP_404_NOT_FOUND)

        # Şifre varsa, şifreyi kontrol et
        if custom_url.password:
            if not password:
                return Response({"error": "Password is required for this URL."}, status=status.HTTP_400_BAD_REQUEST)

            if not check_password(password, custom_url.password):
                return Response({"error": "Invalid password."}, status=status.HTTP_403_FORBIDDEN)

        # Şifre kontrolü başarıyla geçtiyse veya şifre gerekli değilse URL'yi döndür
        return Response({"long_url": custom_url.long_url}, status=status.HTTP_200_OK)


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
                return render(request, 'utility/security.html', context={"msg": "Invalid Password", "short_url": short_url})
        return render(request, 'utility/security.html', context={"msg": "", "short_url": short_url})
    if custom_url.one_time_only:
        custom_url.is_active = False
        custom_url.save()
    return redirect(custom_url.long_url)

# URL-SHORTENER VİEWS: ENDS


# QR-CODE VİEWS: STARTS



# QR-CODE VİEWS: ENDS

