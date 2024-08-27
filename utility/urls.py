from django.urls import path
from . import views


urlpatterns = [
    path('api/urls/', views.URLListCreateView.as_view(), name='url-list-create'),
    path('api/urls/<int:pk>/', views.URLDetailView.as_view(), name='url-detail'),
]
