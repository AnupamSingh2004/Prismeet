from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from .models import User, UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create user profile when user is created
    """
    if created and not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save user profile when user is saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(user_logged_in)
def update_last_login(sender, user, request, **kwargs):
    """
    Update last login timestamp when user logs in
    """
    user.last_login_at = timezone.now()
    user.save(update_fields=['last_login_at'])