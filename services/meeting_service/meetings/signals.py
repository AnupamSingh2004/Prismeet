import logging
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Meeting, MeetingParticipant, MeetingInvitation

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Meeting)
def meeting_created_or_updated(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New meeting created: {instance.title} (ID: {instance.id})")
        # Add host as a participant if they're not already
        MeetingParticipant.objects.get_or_create(
            meeting=instance,
            user_id=instance.host_user_id,
            defaults={
                'name': 'Host',  # This would be replaced with actual name from auth service
                'email': 'host@example.com',  # This would be replaced with actual email from auth service
                'role': 'host'
            }
        )
    else:
        logger.info(f"Meeting updated: {instance.title} (ID: {instance.id})")


@receiver(post_save, sender=MeetingParticipant)
def participant_joined_or_updated(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New participant joined meeting: {instance.name} (Meeting ID: {instance.meeting.id})")
    else:
        # Check if participant has left the meeting
        if instance.left_at and not instance.is_active:
            logger.info(f"Participant left meeting: {instance.name} (Meeting ID: {instance.meeting.id})")


@receiver(post_save, sender=MeetingInvitation)
def invitation_created_or_updated(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New invitation sent for meeting: {instance.meeting.title} to {instance.email}")
    elif instance.status in ['accepted', 'declined']:
        logger.info(f"Invitation {instance.status} by {instance.email} for meeting: {instance.meeting.title}")

