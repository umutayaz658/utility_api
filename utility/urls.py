from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/register/', views.register_view, name='register'),
    path('api/login/', views.login_view, name='login'),
    path('api/logout/', views.logout_view, name='logout'),

    path('api/create_short_url/', views.url_create_view, name='create_short_url'),
    path('api/urls/', views.URLDetailView.as_view(), name='url-list'),
    path('api/get_long_url/', views.get_long_url, name='get_long_url'),
    path('api/update_activity/<str:short_url>/', views.update_url_active_status, name='update_url_active_status'),
    path('api/delete/<str:short_url>/', views.delete_url, name='delete_url'),
    path('api/update_validity/<str:short_url>/', views.update_validity_period, name='update_validity_period'),
    path('<str:short_url>/', views.redirect_to_long_url, name='redirect_to_long_url'),
    path('url/expired/', views.link_expired, name='link_expired'),

    path('api/notes/', views.QuickNoteCreateView.as_view(), name='create_note'),
    path('api/notes/sent/', views.UserSentNotesView.as_view(), name='user-sent-notes'),
    path('api/notes/received/', views.UserReceivedNotesView.as_view(), name='user-received-notes'),
    path('autocomplete/users/', views.UserAutocompleteView.as_view(), name='user_autocomplete_api'),
    path('api/notes/download/<int:note_id>/', views.QuickNoteFileDownloadView.as_view(), name='note_file_download'),

    path('api/token/', views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', views.LogoutView.as_view(), name='auth_logout'),

    path('api/qr-code/', views.QRCodeAPIView.as_view(), name='qr_code_api'),
    path('api/download-qr-code/<str:filename>/', views.download_qr_code, name='download_qr_code'),

    path('api/imagetopdf/', views.ImageToPDFView.as_view(), name='create_pdf'),
    path('api/imagetopdf/download/<int:pk>/', views.DownloadPDFView.as_view(), name='download_pdf'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


