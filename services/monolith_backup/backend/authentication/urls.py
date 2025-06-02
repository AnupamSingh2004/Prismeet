from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # Using DRF's built-in token auth view as a placeholder
    # This can be extended with custom views as needed
    path('token/', obtain_auth_token, name='api_token_auth'),
]
