from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid
import base64

class User(AbstractUser):
    """
    Custom User model with additional fields for Prismeet
    """
    PROVIDER_CHOICES = [
        ('email', 'Email'),
        ('google', 'Google'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    # Store profile picture as binary data instead of URL
    profile_picture_data = models.BinaryField(blank=True, null=True)
    profile_picture_content_type = models.CharField(max_length=50, blank=True, null=True)
    profile_picture_filename = models.CharField(max_length=255, blank=True, null=True)

    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # Authentication related fields
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='email')
    google_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)

    # Password reset
    password_reset_token = models.CharField(max_length=255, blank=True, null=True)
    password_reset_sent_at = models.DateTimeField(blank=True, null=True)

    # Account status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(blank=True, null=True)

    # Meeting preferences
    timezone = models.CharField(max_length=50, default='UTC')
    default_meeting_duration = models.IntegerField(default=60)  # minutes

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def profile_picture_base64(self):
        """Return base64 encoded profile picture for frontend use"""
        if self.profile_picture_data and self.profile_picture_content_type:
            encoded = base64.b64encode(self.profile_picture_data).decode('utf-8')
            return f"data:{self.profile_picture_content_type};base64,{encoded}"
        return None

    def set_profile_picture(self, file_data, content_type, filename):
        """Set profile picture from uploaded file"""
        self.profile_picture_data = file_data
        self.profile_picture_content_type = content_type
        self.profile_picture_filename = filename

    def clear_profile_picture(self):
        """Remove profile picture"""
        self.profile_picture_data = None
        self.profile_picture_content_type = None
        self.profile_picture_filename = None

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    Extended user profile for additional information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    company = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    meeting_reminders = models.BooleanField(default=True)
    recording_notifications = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.email}"


class LoginAttempt(models.Model):
    """
    Track login attempts for security
    """
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{status} login attempt for {self.email} at {self.created_at}"