from django.urls import path
from . import views

urlpatterns = [
    path('api/create_short_url/', views.url_create_view, name='create_short_url'),
    path('api/urls/', views.URLDetailView.as_view(), name='url-list'),
    path('api/get_long_url/', views.get_long_url, name='get_long_url'),
    path('api/update_activity/<str:short_url>/', views.update_url_active_status, name='update_url_active_status'),
    path('api/update_validity/<str:short_url>/', views.update_validity_period, name='update_validity_period'),
    path('<str:short_url>/', views.redirect_to_long_url, name='redirect_to_long_url'),
]
