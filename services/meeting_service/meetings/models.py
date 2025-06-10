from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import secrets
import string


class Meeting(models.Model):
    """
    Main meeting model for Prismeet
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    TYPE_CHOICES = [
        ('instant', 'Instant Meeting'),
        ('scheduled', 'Scheduled Meeting'),
        ('recurring', 'Recurring Meeting'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Meeting identification
    meeting_id = models.CharField(max_length=12, unique=True, blank=True)
    meeting_password = models.CharField(max_length=10, blank=True)

    # Meeting details
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hosted_meetings')
    meeting_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='instant')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    # Timing
    scheduled_start_time = models.DateTimeField(null=True, blank=True)
    scheduled_end_time = models.DateTimeField(null=True, blank=True)
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=60, validators=[MinValueValidator(1), MaxValueValidator(1440)])
    timezone = models.CharField(max_length=50, default='UTC')

    # Settings
    is_recording_enabled = models.BooleanField(default=True)
    is_waiting_room_enabled = models.BooleanField(default=False)
    is_password_protected = models.BooleanField(default=False)
    max_participants = models.IntegerField(default=100, validators=[MinValueValidator(2), MaxValueValidator(1000)])

    # Permissions
    allow_participants_to_mute = models.BooleanField(default=True)
    allow_participants_to_share_screen = models.BooleanField(default=True)
    allow_participants_to_record = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['meeting_id']),
            models.Index(fields=['host', 'status']),
            models.Index(fields=['scheduled_start_time']),
        ]

    def __str__(self):
        return f"{self.title} ({self.meeting_id})"

    def save(self, *args, **kwargs):
        if not self.meeting_id:
            self.meeting_id = self.generate_meeting_id()
        if self.is_password_protected and not self.meeting_password:
            self.meeting_password = self.generate_meeting_password()
        super().save(*args, **kwargs)

    def generate_meeting_id(self):
        """Generate a unique 12-character meeting ID"""
        while True:
            meeting_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            if not Meeting.objects.filter(meeting_id=meeting_id).exists():
                return meeting_id

    def generate_meeting_password(self):
        """Generate a 6-digit meeting password"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))

    @property
    def is_active(self):
        """Check if meeting is currently active"""
        return self.status == 'in_progress'

    @property
    def is_scheduled_for_today(self):
        """Check if meeting is scheduled for today"""
        if not self.scheduled_start_time:
            return False
        return self.scheduled_start_time.date() == timezone.now().date()

    def can_join(self, user):
        """Check if user can join the meeting"""
        if self.status == 'cancelled':
            return False
        if self.host == user:
            return True
        return MeetingParticipant.objects.filter(meeting=self, user=user).exists()

    def start_meeting(self):
        """Start the meeting"""
        if self.status != 'in_progress':
            self.status = 'in_progress'
            self.actual_start_time = timezone.now()
            self.save()

    def end_meeting(self):
        """End the meeting"""
        if self.status == 'in_progress':
            self.status = 'completed'
            self.actual_end_time = timezone.now()
            self.save()


class MeetingParticipant(models.Model):
    """
    Participants in a meeting
    """
    ROLE_CHOICES = [
        ('host', 'Host'),
        ('co_host', 'Co-Host'),
        ('participant', 'Participant'),
    ]

    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('joined', 'Joined'),
        ('left', 'Left'),
        ('waiting', 'Waiting Room'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meeting_participations')

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='invited')

    # Join/Leave tracking
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)

    # Permissions
    can_mute_others = models.BooleanField(default=False)
    can_share_screen = models.BooleanField(default=True)
    can_record = models.BooleanField(default=False)

    # Audio/Video status
    is_audio_muted = models.BooleanField(default=False)
    is_video_disabled = models.BooleanField(default=False)
    is_screen_sharing = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['meeting', 'user']
        indexes = [
            models.Index(fields=['meeting', 'status']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.user.full_name} in {self.meeting.title}"

    def join_meeting(self):
        """Mark participant as joined"""
        self.status = 'joined'
        self.joined_at = timezone.now()
        self.save()

    def leave_meeting(self):
        """Mark participant as left"""
        self.status = 'left'
        self.left_at = timezone.now()
        self.save()


class MeetingInvitation(models.Model):
    """
    Meeting invitations sent to participants
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invitations')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    invitation_token = models.CharField(max_length=255, unique=True)

    # Optional message
    message = models.TextField(blank=True)

    # Timestamps
    sent_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['meeting', 'email']
        indexes = [
            models.Index(fields=['invitation_token']),
            models.Index(fields=['meeting', 'status']),
        ]

    def __str__(self):
        return f"Invitation to {self.email} for {self.meeting.title}"

    def save(self, *args, **kwargs):
        if not self.invitation_token:
            self.invitation_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        super().save(*args, **kwargs)

    def accept(self):
        """Accept the invitation"""
        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()

    def decline(self):
        """Decline the invitation"""
        self.status = 'declined'
        self.responded_at = timezone.now()
        self.save()


class MeetingRecording(models.Model):
    """
    Meeting recordings storage information
    """
    STATUS_CHOICES = [
        ('recording', 'Recording'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
        ('deleted', 'Deleted'),
    ]

    QUALITY_CHOICES = [
        ('720p', '720p HD'),
        ('1080p', '1080p Full HD'),
        ('4k', '4K Ultra HD'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='recordings')

    # Recording details
    title = models.CharField(max_length=200)
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES, default='1080p')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recording')

    # File information
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    file_path = models.CharField(max_length=500, blank=True)  # Path to storage

    # Timestamps
    recording_started_at = models.DateTimeField()
    recording_ended_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-recording_started_at']
        indexes = [
            models.Index(fields=['meeting', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Recording of {self.meeting.title} - {self.get_status_display()}"

    @property
    def file_size_mb(self):
        """Return file size in MB"""
        if self.file_size_bytes:
            return round(self.file_size_bytes / (1024 * 1024), 2)
        return 0

    @property
    def duration_formatted(self):
        """Return formatted duration"""
        if not self.duration_seconds:
            return "0:00"

        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"


class MeetingChat(models.Model):
    """
    Chat messages during meetings
    """
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text Message'),
        ('system', 'System Message'),
        ('file', 'File Share'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='chat_messages')
    participant = models.ForeignKey(MeetingParticipant, on_delete=models.CASCADE, related_name='chat_messages')

    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField()

    # For file sharing
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    file_path = models.CharField(max_length=500, blank=True)

    # Metadata
    is_private = models.BooleanField(default=False)  # Private message to host
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['meeting', 'created_at']),
            models.Index(fields=['participant']),
        ]

    def __str__(self):
        return f"Chat in {self.meeting.title} by {self.participant.user.full_name}"


class MeetingSettings(models.Model):
    """
    User-specific meeting settings and preferences
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meeting_settings')

    # Default meeting settings
    default_meeting_duration = models.IntegerField(default=60)
    default_max_participants = models.IntegerField(default=100)
    auto_record = models.BooleanField(default=True)
    auto_mute_participants = models.BooleanField(default=False)
    enable_waiting_room = models.BooleanField(default=False)

    # Notification preferences
    email_meeting_reminders = models.BooleanField(default=True)
    email_recording_ready = models.BooleanField(default=True)
    email_meeting_invitations = models.BooleanField(default=True)

    # Video/Audio defaults
    default_video_quality = models.CharField(max_length=10, choices=MeetingRecording.QUALITY_CHOICES, default='1080p')
    join_with_video_off = models.BooleanField(default=False)
    join_with_audio_muted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Meeting settings for {self.user.full_name}"