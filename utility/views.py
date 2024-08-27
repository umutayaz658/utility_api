from django.shortcuts import render
from rest_framework import generics
from .models import CustomURL
from .serializers import URLSerializer

# URL-SHORTENER VİEWS: STARTS.


class URLListCreateView(generics.ListCreateAPIView):
    queryset = CustomURL.objects.all()
    serializer_class = URLSerializer


class URLDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomURL.objects.all()
    serializer_class = URLSerializer

# URL-SHORTENER VİEWS: ENDS

