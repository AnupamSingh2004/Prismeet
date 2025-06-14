from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Simple Health Check
    path('health/', views.health_check, name='health'),

    # Authentication endpoints
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('google-auth/', views.google_auth, name='google_auth'),

    # Profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),

    # Profile picture endpoints
    path('profile/picture/upload/', views.upload_profile_picture, name='upload_profile_picture'),
    path('profile/picture/delete/', views.delete_profile_picture, name='delete_profile_picture'),
    path('profile/picture/', views.get_profile_picture, name='get_profile_picture'),

    # Password management
    path('change-password/', views.change_password, name='change_password'),
    path('password-reset-request/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/', views.password_reset_confirm, name='password_reset_confirm'),

    # Email verification
    path('verify-email/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),

    # Token verification for inter-service communication
    path('verify-token/', views.verify_token, name='verify_token'),
]