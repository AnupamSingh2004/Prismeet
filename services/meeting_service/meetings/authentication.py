import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import logging

logger = logging.getLogger(__name__)


class GoogleOAuthUser:
    """
    Custom user class to represent Google OAuth users in meeting service
    """
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.email = user_data.get('email')
        self.first_name = user_data.get('first_name', '')
        self.last_name = user_data.get('last_name', '')
        self.full_name = user_data.get('full_name', f"{self.first_name} {self.last_name}".strip())
        self.is_authenticated = True
        self.is_active = user_data.get('is_active', True)
        self.is_staff = user_data.get('is_staff', False)
        self.is_superuser = user_data.get('is_superuser', False)
        self.profile_picture = user_data.get('profile_picture')
        
    def get_full_name(self):
        return self.full_name
        
    def get_short_name(self):
        return self.first_name
        
    def __str__(self):
        return self.email


class GoogleOAuthAuthentication(BaseAuthentication):
    """
    Authentication class for Google OAuth tokens via auth service
    """
    
    def authenticate(self, request):
        # Check for Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None
            
        # Support both Bearer and Token formats
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        elif auth_header.startswith('Token '):
            token = auth_header.split(' ')[1]
        else:
            return None
            
        try:
            # Verify token with auth service
            response = requests.get(
                f"{settings.AUTH_SERVICE_URL}/api/auth/verify-token/",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                user = GoogleOAuthUser(user_data)
                return (user, token)
            elif response.status_code == 401:
                raise AuthenticationFailed('Invalid or expired token')
            else:
                logger.error(f"Auth service returned {response.status_code}")
                raise AuthenticationFailed('Authentication service error')
                
        except requests.RequestException as e:
            logger.error(f"Auth service request failed: {e}")
            raise AuthenticationFailed('Authentication service unavailable')
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise AuthenticationFailed('Authentication failed')

    def authenticate_header(self, request):
        return 'Bearer'


class GoogleOAuthBackend(BaseBackend):
    """
    Authentication backend for Google OAuth
    """
    
    def authenticate(self, request, token=None, **kwargs):
        if not token:
            return None
            
        try:
            response = requests.get(
                f"{settings.AUTH_SERVICE_URL}/api/auth/verify-token/",
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return GoogleOAuthUser(user_data)
        except Exception as e:
            logger.error(f"Backend authentication error: {e}")
            
        return None

    def get_user(self, user_id):
        # For meeting service, we don't store users locally
        return None


class OptionalAuthentication(BaseAuthentication):
    """
    Authentication that allows both authenticated and anonymous users
    Useful for meeting join endpoints that support guests
    """
    
    def authenticate(self, request):
        # Try Google OAuth first
        oauth_auth = GoogleOAuthAuthentication()
        result = oauth_auth.authenticate(request)
        
        if result:
            return result
            
        # Return None to allow anonymous access
        return None