from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('api/create_short_url/', views.url_create_view, name='create_short_url'),
    path('api/urls/', views.URLDetailView.as_view(), name='url-list'),
    path('api/get_long_url/', views.get_long_url, name='get_long_url'),
    path('api/update_activity/<str:short_url>/', views.update_url_active_status, name='update_url_active_status'),
    path('api/update_validity/<str:short_url>/', views.update_validity_period, name='update_validity_period'),
    path('<str:short_url>/', views.redirect_to_long_url, name='redirect_to_long_url'),
    path('api/notes/', views.QuickNoteCreateView.as_view(), name='create_note'),
    path('api/notes/sent/', views.UserSentNotesView.as_view(), name='user-sent-notes'),
    path('api/notes/received/', views.UserReceivedNotesView.as_view(), name='user-received-notes'),
    path('api/token/', views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', views.LogoutView.as_view(), name='auth_logout'),
]


