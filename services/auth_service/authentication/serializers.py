from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from .models import User, UserProfile
import secrets
import string
import logging

logger = logging.getLogger(__name__)

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'confirm_password', 'phone_number']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        # Generate email verification token
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number', ''),
            email_verification_token=token,
            email_verification_sent_at=timezone.now(),
            is_email_verified=False,
            provider='email'
        )

        # Create user profile
        UserProfile.objects.get_or_create(user=user)

        # Send verification email
        self.send_verification_email(user)

        return user

    def send_verification_email(self, user):
        """Send verification email to the user"""
        try:
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={user.email_verification_token}"

            subject = "Verify your Prismeet account"
            message = f"""
            Hi {user.first_name},
            
            Thank you for signing up for Prismeet! Please click the link below to verify your email address:
            
            {verification_url}
            
            If you didn't create this account, please ignore this email.
            
            Best regards,
            The Prismeet Team
            """

            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            logger.info(f"Sending verification email to {user.email}")
            logger.info(f"Using email backend: {settings.EMAIL_BACKEND}")
            logger.info(f"From email: {from_email}")

            # Send the email
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )

            logger.info(f"Verification email sent successfully to {user.email}")

        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
            # Don't raise the exception to avoid registration failure
            # but log it for debugging


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)

            if not user:
                raise serializers.ValidationError("Invalid email or password.")

            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("Must provide email and password.")


class GoogleAuthSerializer(serializers.Serializer):
    """
    Serializer for Google OAuth
    """
    google_token = serializers.CharField()

    def validate_google_token(self, value):
        # This will be implemented in the view with Google OAuth library
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile
    """
    full_name = serializers.ReadOnlyField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'profile_picture', 'phone_number', 'timezone',
            'default_meeting_duration', 'is_email_verified',
            'provider', 'created_at', 'last_login_at', 'profile'
        ]
        read_only_fields = ['id', 'email', 'provider', 'created_at', 'is_email_verified']

    def get_profile(self, obj):
        try:
            profile = obj.profile
            return {
                'bio': profile.bio,
                'company': profile.company,
                'job_title': profile.job_title,
                'website': profile.website,
                'email_notifications': profile.email_notifications,
                'meeting_reminders': profile.meeting_reminders,
                'recording_notifications': profile.recording_notifications,
            }
        except UserProfile.DoesNotExist:
            return None

    def to_representation(self, instance):
        """
        Customize the representation to ensure profile_picture is always included
        """
        data = super().to_representation(instance)

        # Ensure profile_picture is included even if it's an empty string
        if 'profile_picture' not in data or data['profile_picture'] is None:
            data['profile_picture'] = ''

        return data

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile fields
        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance

class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation
    """
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification
    """
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            user = User.objects.get(email_verification_token=value)
            if user.is_email_verified:
                raise serializers.ValidationError("Email is already verified.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token.")
        return value