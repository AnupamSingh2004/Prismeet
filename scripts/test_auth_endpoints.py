import requests
import json
import time
from datetime import datetime

# Configuration
AUTH_SERVICE_URL = "http://localhost:8001"
BACKEND_URL = "http://localhost:8000"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"{'='*60}")

def print_response(response, description="Response"):
    print(f"\n{description}:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Body: {response.text}")

def test_health_check():
    """Test if the authentication service is running"""
    print_test_header("Health Check")

    try:
        # Test auth service health
        response = requests.get(f"{AUTH_SERVICE_URL}/api/auth/", timeout=10)
        print_response(response, "Auth Service Health Check")

        # Test backend health
        response = requests.get(f"{BACKEND_URL}/api/", timeout=10)
        print_response(response, "Backend Health Check")

        return True
    except requests.exceptions.RequestException as e:
        print(f"Health check failed: {e}")
        return False

def test_user_registration():
    """Test user registration endpoint"""
    print_test_header("User Registration")

    test_user = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }

    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/api/auth/register/",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "Registration Response")

        if response.status_code == 201:
            return test_user, response.json()
        else:
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Registration failed: {e}")
        return None, None

def test_user_login(user_data):
    """Test user login endpoint"""
    print_test_header("User Login")

    if not user_data:
        print("Skipping login test - no user data available")
        return None

    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }

    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/api/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "Login Response")

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Login failed: {e}")
        return None

def test_google_auth():
    """Test Google OAuth endpoints"""
    print_test_header("Google OAuth")

    try:
        # Test Google auth initiation
        response = requests.get(f"{AUTH_SERVICE_URL}/api/auth/google-auth/")
        print_response(response, "Google Auth Initiation")

    except requests.exceptions.RequestException as e:
        print(f"Google auth test failed: {e}")

def test_profile_access(auth_token):
    """Test profile access with authentication"""
    print_test_header("Profile Access")

    if not auth_token:
        print("Skipping profile test - no auth token available")
        return

    headers = {
        "Authorization": f"Bearer {auth_token.get('access', '')}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{AUTH_SERVICE_URL}/api/auth/profile/",
            headers=headers
        )
        print_response(response, "Profile Access Response")

    except requests.exceptions.RequestException as e:
        print(f"Profile access failed: {e}")

def test_password_change(auth_token):
    """Test password change endpoint"""
    print_test_header("Password Change")

    if not auth_token:
        print("Skipping password change test - no auth token available")
        return

    headers = {
        "Authorization": f"Bearer {auth_token.get('access', '')}",
        "Content-Type": "application/json"
    }

    password_data = {
        "old_password": "TestPassword123!",
        "new_password": "NewTestPassword123!"
    }

    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/api/auth/change-password/",
            json=password_data,
            headers=headers
        )
        print_response(response, "Password Change Response")

    except requests.exceptions.RequestException as e:
        print(f"Password change failed: {e}")

def test_password_reset():
    """Test password reset request endpoint"""
    print_test_header("Password Reset Request")

    reset_data = {
        "email": "test@example.com"
    }

    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/api/auth/password-reset-request/",
            json=reset_data,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "Password Reset Request Response")

    except requests.exceptions.RequestException as e:
        print(f"Password reset request failed: {e}")

def test_email_verification():
    """Test email verification endpoints"""
    print_test_header("Email Verification")

    verify_data = {
        "email": "test@example.com"
    }

    try:
        # Test verification email sending
        response = requests.post(
            f"{AUTH_SERVICE_URL}/api/auth/verify-email/",
            json=verify_data,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "Send Verification Email Response")

        # Test resend verification
        response = requests.post(
            f"{AUTH_SERVICE_URL}/api/auth/resend-verification/",
            json=verify_data,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "Resend Verification Email Response")

    except requests.exceptions.RequestException as e:
        print(f"Email verification test failed: {e}")

def test_logout(auth_token):
    """Test user logout endpoint"""
    print_test_header("User Logout")

    if not auth_token:
        print("Skipping logout test - no auth token available")
        return

    headers = {
        "Authorization": f"Bearer {auth_token.get('access', '')}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/api/auth/logout/",
            headers=headers
        )
        print_response(response, "Logout Response")

    except requests.exceptions.RequestException as e:
        print(f"Logout failed: {e}")

def main():
    """Run all authentication tests"""
    print(f"Starting Authentication Service Tests at {datetime.now()}")
    print(f"Auth Service URL: {AUTH_SERVICE_URL}")
    print(f"Backend URL: {BACKEND_URL}")

    # Run tests
    if not test_health_check():
        print("Services are not running. Please start Docker containers first.")
        return

    # Test registration
    user_data, registration_response = test_user_registration()

    # Test login
    auth_token = test_user_login(user_data)

    # Test Google OAuth
    test_google_auth()

    # Test authenticated endpoints
    test_profile_access(auth_token)
    test_password_change(auth_token)

    # Test password reset
    test_password_reset()

    # Test email verification
    test_email_verification()

    # Test logout
    test_logout(auth_token)

    print(f"\n{'='*60}")
    print("All tests completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()