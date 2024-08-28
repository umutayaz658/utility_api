from django.urls import path
from . import views

urlpatterns = [
    path('api/urls/', views.URLListCreateView.as_view(), name='url-list-create'),
    path('api/urls/<int:pk>/', views.URLDetailView.as_view(), name='url-detail'),
    path('api/get_long_url/', views.GetLongURLView.as_view(), name='get_long_url'),
    path('<str:short_url>/', views.redirect_to_long_url, name='redirect_to_long_url'),
]
