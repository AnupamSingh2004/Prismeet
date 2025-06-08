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
import base64
from PIL import Image
import io

logger = logging.getLogger(__name__)

class ProfilePictureUploadSerializer(serializers.Serializer):
    """
    Serializer for profile picture upload
    """
    profile_picture = serializers.CharField()  # Base64 encoded image

    def validate_profile_picture(self, value):
        try:
            # Check if it's a valid base64 data URL
            if not value.startswith('data:image/'):
                raise serializers.ValidationError("Invalid image format. Must be a data URL.")

            # Extract content type and base64 data
            header, data = value.split(',', 1)
            content_type = header.split(':')[1].split(';')[0]

            # Validate content type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if content_type not in allowed_types:
                raise serializers.ValidationError(
                    f"Unsupported image type. Allowed: {', '.join(allowed_types)}"
                )

            # Decode base64 data
            try:
                image_data = base64.b64decode(data)
            except Exception:
                raise serializers.ValidationError("Invalid base64 data.")

            # Validate image size (max 5MB)
            if len(image_data) > 5 * 1024 * 1024:
                raise serializers.ValidationError("Image size must be less than 5MB.")

            # Validate that it's actually an image using PIL
            try:
                image = Image.open(io.BytesIO(image_data))
                image.verify()
            except Exception:
                raise serializers.ValidationError("Invalid image file.")

            return {
                'data': image_data,
                'content_type': content_type,
                'size': len(image_data)
            }

        except ValueError as e:
            raise serializers.ValidationError("Invalid image format.")

    def save(self, user):
        validated_data = self.validated_data['profile_picture']

        # Resize image if too large (optional optimization)
        image_data = self._resize_image_if_needed(
            validated_data['data'],
            validated_data['content_type']
        )

        # Set profile picture
        user.set_profile_picture(
            file_data=image_data,
            content_type=validated_data['content_type'],
            filename=f"profile_{user.id}.{validated_data['content_type'].split('/')[-1]}"
        )
        user.save()
        return user

    def _resize_image_if_needed(self, image_data, content_type, max_size=(800, 800)):
        """Resize image if it's too large"""
        try:
            image = Image.open(io.BytesIO(image_data))

            # Only resize if image is larger than max_size
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Save resized image to bytes
                output = io.BytesIO()
                format_map = {
                    'image/jpeg': 'JPEG',
                    'image/jpg': 'JPEG',
                    'image/png': 'PNG',
                    'image/gif': 'GIF',
                    'image/webp': 'WEBP'
                }

                image_format = format_map.get(content_type, 'JPEG')

                # Convert RGBA to RGB for JPEG
                if image_format == 'JPEG' and image.mode == 'RGBA':
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1] if len(image.split()) == 4 else None)
                    image = background

                image.save(output, format=image_format, quality=85, optimize=True)
                return output.getvalue()

            return image_data

        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            return image_data


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
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'profile_picture', 'phone_number', 'timezone',
            'default_meeting_duration', 'is_email_verified',
            'provider', 'created_at', 'last_login_at', 'profile'
        ]
        read_only_fields = ['id', 'email', 'provider', 'created_at', 'is_email_verified']

    def get_profile_picture(self, obj):
        """Return base64 encoded profile picture or None"""
        return obj.profile_picture_base64

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