from django.db import models
from django.utils import timezone
import uuid
import json


class Meeting(models.Model):
    """
    Main meeting model
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    ]

    MEETING_TYPE_CHOICES = [
        ('instant', 'Instant Meeting'),
        ('scheduled', 'Scheduled Meeting'),
        ('recurring', 'Recurring Meeting'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    # Host information (UUID from auth service)
    host_id = models.UUIDField()
    host_email = models.EmailField()
    host_name = models.CharField(max_length=100)

    # Meeting details
    meeting_id = models.CharField(max_length=20, unique=True)  # 6-digit meeting ID
    passcode = models.CharField(max_length=10, blank=True, null=True)
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='instant')

    # Scheduling
    scheduled_start = models.DateTimeField(blank=True, null=True)
    scheduled_end = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.IntegerField(default=60)
    timezone = models.CharField(max_length=50, default='UTC')

    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    actual_start = models.DateTimeField(blank=True, null=True)
    actual_end = models.DateTimeField(blank=True, null=True)

    # Settings
    waiting_room_enabled = models.BooleanField(default=True)
    join_before_host = models.BooleanField(default=False)
    mute_participants_on_join = models.BooleanField(default=True)
    allow_screen_sharing = models.BooleanField(default=True)
    allow_recording = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=100)

    # WebRTC Room Configuration
    room_config = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'meetings'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.meeting_id})"

    def is_active(self):
        return self.status == 'ongoing'

    def can_join(self):
        return self.status in ['scheduled', 'ongoing']

    def get_join_url(self):
        return f"/meeting/{self.meeting_id}"


class MeetingParticipant(models.Model):
    """
    Track meeting participants
    """
    ROLE_CHOICES = [
        ('host', 'Host'),
        ('co_host', 'Co-Host'),
        ('participant', 'Participant'),
        ('viewer', 'Viewer'),
    ]

    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('joined', 'Joined'),
        ('left', 'Left'),
        ('removed', 'Removed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='participants')

    # Participant info (from auth service or guest)
    user_id = models.UUIDField(blank=True, null=True)  # None for guests
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=100)
    is_guest = models.BooleanField(default=False)

    # WebRTC connection info
    peer_id = models.CharField(max_length=100, blank=True, null=True)
    socket_id = models.CharField(max_length=100, blank=True, null=True)

    # Participant status
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='invited')

    # Media status
    audio_enabled = models.BooleanField(default=True)
    video_enabled = models.BooleanField(default=True)
    screen_sharing = models.BooleanField(default=False)

    # Timing
    joined_at = models.DateTimeField(blank=True, null=True)
    left_at = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.IntegerField(default=0)

    # Connection details
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'meeting_participants'
        unique_together = ['meeting', 'user_id']
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.name} in {self.meeting.title}"

    def join_meeting(self):
        self.status = 'joined'
        self.joined_at = timezone.now()
        self.save()

    def leave_meeting(self):
        self.status = 'left'
        self.left_at = timezone.now()
        if self.joined_at:
            self.duration_seconds = int((self.left_at - self.joined_at).total_seconds())
        self.save()


class MeetingInvitation(models.Model):
    """
    Meeting invitations
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='invitations')

    # Invitee info
    invitee_email = models.EmailField()
    invitee_name = models.CharField(max_length=100, blank=True, null=True)
    invitee_user_id = models.UUIDField(blank=True, null=True)

    # Invitation details
    invitation_token = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, null=True)

    # Timing
    sent_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'meeting_invitations'
        unique_together = ['meeting', 'invitee_email']

    def __str__(self):
        return f"Invitation to {self.invitee_email} for {self.meeting.title}"


class WebRTCSession(models.Model):
    """
    Track WebRTC sessions for debugging and monitoring
    """
    SESSION_STATUS_CHOICES = [
        ('connecting', 'Connecting'),
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='webrtc_sessions')
    participant = models.ForeignKey(MeetingParticipant, on_delete=models.CASCADE, related_name='webrtc_sessions')

    # WebRTC details
    peer_id = models.CharField(max_length=100)
    session_id = models.CharField(max_length=100)
    ice_servers = models.JSONField(default=list)

    # Connection status
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='connecting')
    connection_state = models.CharField(max_length=50, blank=True, null=True)
    ice_connection_state = models.CharField(max_length=50, blank=True, null=True)

    # Media tracks
    local_tracks = models.JSONField(default=list)
    remote_tracks = models.JSONField(default=list)

    # Quality metrics
    stats_data = models.JSONField(default=dict, blank=True)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'webrtc_sessions'
        ordering = ['-started_at']

    def __str__(self):
        return f"WebRTC Session {self.session_id} for {self.participant.name}"


class MeetingRecording(models.Model):
    """
    Meeting recordings metadata
    """
    RECORDING_STATUS_CHOICES = [
        ('starting', 'Starting'),
        ('recording', 'Recording'),
        ('stopping', 'Stopping'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='recordings')

    # Recording details
    recording_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=RECORDING_STATUS_CHOICES, default='starting')

    # File information
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(default=0)
    duration_seconds = models.IntegerField(default=0)
    format = models.CharField(max_length=20, default='webm')

    # Metadata
    started_by = models.UUIDField()  # User ID who started recording
    started_by_name = models.CharField(max_length=100)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    # Processing
    processing_status = models.CharField(max_length=50, default='pending')
    download_url = models.URLField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'meeting_recordings'
        ordering = ['-started_at']

    def __str__(self):
        return f"Recording {self.recording_id} for {self.meeting.title}"


class MeetingAnalytics(models.Model):
    """
    Meeting analytics and statistics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.OneToOneField(Meeting, on_delete=models.CASCADE, related_name='analytics')

    # Participation metrics
    total_participants = models.IntegerField(default=0)
    max_concurrent_participants = models.IntegerField(default=0)
    average_duration_seconds = models.IntegerField(default=0)

    # Audio/Video metrics
    total_audio_time_seconds = models.BigIntegerField(default=0)
    total_video_time_seconds = models.BigIntegerField(default=0)
    screen_sharing_duration_seconds = models.IntegerField(default=0)

    # Quality metrics
    average_connection_quality = models.FloatField(default=0.0)
    connection_issues_count = models.IntegerField(default=0)

    # Engagement metrics
    chat_messages_count = models.IntegerField(default=0)
    reactions_count = models.IntegerField(default=0)

    # Technical metrics
    total_bandwidth_mb = models.FloatField(default=0.0)
    peak_bandwidth_mbps = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'meeting_analytics'

    def __str__(self):
        return f"Analytics for {self.meeting.title}"