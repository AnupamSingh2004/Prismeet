from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from google.oauth2 import id_token
from google.auth.transport import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import secrets
import string

from .models import User, UserProfile, LoginAttempt
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    GoogleAuthSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer
)

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_login_attempt(email, ip_address, user_agent, success=False):
    """Log login attempt"""
    LoginAttempt.objects.create(
        email=email,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """
    Register a new user
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            user = serializer.save()

            # Send verification email
            send_verification_email(user)

            # Create token
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'message': 'Registration successful. Please check your email to verify your account.',
                'user': UserProfileSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    Login user
    """
    serializer = UserLoginSerializer(data=request.data)
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    if serializer.is_valid():
        user = serializer.validated_data['user']

        # Update last login
        user.last_login_at = timezone.now()
        user.save()

        # Log successful attempt
        log_login_attempt(user.email, ip_address, user_agent, success=True)

        # Login user
        login(request, user)

        # Get or create token
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_200_OK)

    # Log failed attempt
    email = request.data.get('email', '')
    if email:
        log_login_attempt(email, ip_address, user_agent, success=False)

    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def google_auth(request):
    """
    Google OAuth authentication
    """
    serializer = GoogleAuthSerializer(data=request.data)
    if serializer.is_valid():
        google_token = serializer.validated_data['google_token']

        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                google_token,
                requests.Request(),
                settings.GOOGLE_OAUTH2_CLIENT_ID
            )

            # Extract user information
            google_id = idinfo['sub']
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            profile_picture = idinfo.get('picture', '')

            # Check if user exists
            try:
                user = User.objects.get(email=email)
                # Update Google info and profile picture for existing users
                user_updated = False

                if not user.google_id:
                    user.google_id = google_id
                    user.provider = 'google'
                    user.is_email_verified = True
                    user_updated = True

                # Always update profile picture if available from Google
                if profile_picture and user.profile_picture != profile_picture:
                    user.profile_picture = profile_picture
                    user_updated = True

                # Update first/last name if they're empty
                if not user.first_name and first_name:
                    user.first_name = first_name
                    user_updated = True

                if not user.last_name and last_name:
                    user.last_name = last_name
                    user_updated = True

                if user_updated:
                    user.save()

            except User.DoesNotExist:
                # Create new user
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        google_id=google_id,
                        profile_picture=profile_picture,  # Make sure this is set
                        provider='google',
                        is_email_verified=True,
                        is_active=True
                    )
                    # Create profile
                    UserProfile.objects.create(user=user)

            # Update last login
            user.last_login_at = timezone.now()
            user.save()

            # Log successful attempt
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            log_login_attempt(email, ip_address, user_agent, success=True)

            # Login user
            login(request, user)

            # Get or create token
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'message': 'Google authentication successful',
                'user': UserProfileSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({
                'error': 'Invalid Google token'
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Logout user
    """
    try:
        # Delete token
        request.user.auth_token.delete()
    except:
        pass

    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    Change user password
    """
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        # Update token
        try:
            user.auth_token.delete()
        except:
            pass
        token = Token.objects.create(user=user)

        return Response({
            'message': 'Password changed successfully',
            'token': token.key
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_request(request):
    """
    Request password reset
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        # Generate reset token
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        user.password_reset_token = token
        user.password_reset_sent_at = timezone.now()
        user.save()

        # Send reset email
        send_password_reset_email(user)

        return Response({
            'message': 'Password reset email sent successfully'
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    """
    Confirm password reset
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(password_reset_token=token)

            # Check if token is still valid (24 hours)
            if (timezone.now() - user.password_reset_sent_at).total_seconds() > 86400:
                return Response({
                    'error': 'Password reset token has expired'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Update password
            user.set_password(new_password)
            user.password_reset_token = None
            user.password_reset_sent_at = None
            user.save()

            return Response({
                'message': 'Password reset successful'
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                'error': 'Invalid reset token'
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    """
    Verify email address
    """
    serializer = EmailVerificationSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']

        try:
            user = User.objects.get(email_verification_token=token)
            user.is_email_verified = True
            user.email_verification_token = None
            user.email_verification_sent_at = None
            user.save()

            return Response({
                'message': 'Email verified successfully'
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                'error': 'Invalid verification token'
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resend_verification_email(request):
    """
    Resend email verification
    """
    user = request.user

    if user.is_email_verified:
        return Response({
            'message': 'Email is already verified'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Generate new token
    token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    user.email_verification_token = token
    user.email_verification_sent_at = timezone.now()
    user.save()

    # Send verification email
    send_verification_email(user)

    return Response({
        'message': 'Verification email sent successfully'
    }, status=status.HTTP_200_OK)


def send_verification_email(user):
    """
    Send email verification email
    """
    subject = 'Verify your Prismeet account'
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={user.email_verification_token}"
    message = f"""
    Hi {user.first_name},
    
    Thank you for signing up for Prismeet! Please click the link below to verify your email address:
    
    {verification_link}
    
    If you didn't create this account, please ignore this email.
    
    Best regards,
    The Prismeet Team
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_password_reset_email(user):
    """
    Send password reset email
    """
    subject = 'Reset your Prismeet password'
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={user.password_reset_token}"
    message = f"""
    Hi {user.first_name},
    
    You requested to reset your password for your Prismeet account. Click the link below to set a new password:
    
    {reset_link}
    
    This link will expire in 24 hours. If you didn't request this, please ignore this email.
    
    Best regards,
    The Prismeet Team
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

@require_http_methods(["GET"])
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'auth_service'
    })