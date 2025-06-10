from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import (
    Meeting, MeetingParticipant, MeetingInvitation,
    MeetingRecording, MeetingChat, MeetingSettings
)
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class MeetingParticipantSerializer(serializers.ModelSerializer):
    """
    Serializer for meeting participants
    """
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_profile_picture = serializers.CharField(source='user.profile_picture_base64', read_only=True)

    class Meta:
        model = MeetingParticipant
        fields = [
            'id', 'user', 'user_name', 'user_email', 'user_profile_picture',
            'role', 'status', 'joined_at', 'left_at', 'can_mute_others',
            'can_share_screen', 'can_record', 'is_audio_muted',
            'is_video_disabled', 'is_screen_sharing', 'created_at'
        ]
        read_only_fields = ['id', 'joined_at', 'left_at', 'created_at']


class MeetingListSerializer(serializers.ModelSerializer):
    """
    Serializer for meeting list view (lightweight)
    """
    host_name = serializers.CharField(source='host.full_name', read_only=True)
    participant_count = serializers.SerializerMethodField()
    is_live = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = [
            'id', 'meeting_id', 'title', 'description', 'host', 'host_name',
            'meeting_type', 'status', 'scheduled_start_time', 'scheduled_end_time',
            'duration_minutes', 'is_recording_enabled', 'is_password_protected',
            'participant_count', 'is_live', 'can_join', 'created_at'
        ]

    def get_participant_count(self, obj):
        return obj.participants.filter(status='joined').count()

    def get_is_live(self, obj):
        return obj.status == 'in_progress'

    def get_can_join(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_join(request.user)
        return False


class MeetingDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed meeting view
    """
    host_name = serializers.CharField(source='host.full_name', read_only=True)
    host_email = serializers.CharField(source='host.email', read_only=True)
    participants = MeetingParticipantSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    active_participant_count = serializers.SerializerMethodField()
    is_live = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()
    join_url = serializers.SerializerMethodField()
    recording_count = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = [
            'id', 'meeting_id', 'title', 'description', 'host', 'host_name', 'host_email',
            'meeting_type', 'status', 'scheduled_start_time', 'scheduled_end_time',
            'actual_start_time', 'actual_end_time', 'duration_minutes', 'timezone',
            'is_recording_enabled', 'is_waiting_room_enabled', 'is_password_protected',
            'meeting_password', 'max_participants', 'allow_participants_to_mute',
            'allow_participants_to_share_screen', 'allow_participants_to_record',
            'participants', 'participant_count', 'active_participant_count',
            'is_live', 'can_join', 'join_url', 'recording_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'meeting_id', 'host', 'actual_start_time', 'actual_end_time',
            'created_at', 'updated_at'
        ]

    def get_participant_count(self, obj):
        return obj.participants.count()

    def get_active_participant_count(self, obj):
        return obj.participants.filter(status='joined').count()

    def get_is_live(self, obj):
        return obj.status == 'in_progress'

    def get_can_join(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_join(request.user)
        return False

    def get_join_url(self, obj):
        request = self.context.get('request')
        if request:
            base_url = request.build_absolute_uri('/').rstrip('/')
            return f"{base_url}/meeting/{obj.meeting_id}"
        return None

    def get_recording_count(self, obj):
        return obj.recordings.filter(status='ready').count()


class MeetingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating meetings
    """
    participant_emails = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Meeting
        fields = [
            'title', 'description', 'meeting_type', 'scheduled_start_time',
            'scheduled_end_time', 'duration_minutes', 'timezone', 'is_recording_enabled',
            'is_waiting_room_enabled', 'is_password_protected', 'max_participants',
            'allow_participants_to_mute', 'allow_participants_to_share_screen',
            'allow_participants_to_record', 'participant_emails'
        ]

    def validate(self, attrs):
        # Validate scheduled times
        if attrs.get('scheduled_start_time') and attrs.get('scheduled_end_time'):
            if attrs['scheduled_end_time'] <= attrs['scheduled_start_time']:
                raise serializers.ValidationError("End time must be after start time.")

        # Validate start time is not in the past for scheduled meetings
        if attrs.get('meeting_type') == 'scheduled' and attrs.get('scheduled_start_time'):
            if attrs['scheduled_start_time'] <= timezone.now():
                raise serializers.ValidationError("Scheduled time must be in the future.")

        return attrs

    def create(self, validated_data):
        participant_emails = validated_data.pop('participant_emails', [])
        request = self.context.get('request')

        # Set host as current user
        validated_data['host'] = request.user

        # Create meeting
        meeting = Meeting.objects.create(**validated_data)

        # Add host as participant
        MeetingParticipant.objects.create(
            meeting=meeting,
            user=request.user,
            role='host',
            can_mute_others=True,
            can_share_screen=True,
            can_record=True
        )

        # Send invitations
        if participant_emails:
            self._send_invitations(meeting, participant_emails, request.user)

        return meeting

    def _send_invitations(self, meeting, emails, invited_by):
        """Send meeting invitations"""
        for email in emails:
            try:
                invitation = MeetingInvitation.objects.create(
                    meeting=meeting,
                    email=email,
                    invited_by=invited_by
                )
                # TODO: Send email invitation
                logger.info(f"Invitation sent to {email} for meeting {meeting.meeting_id}")
            except Exception as e:
                logger.error(f"Failed to send invitation to {email}: {str(e)}")


class MeetingUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating meetings
    """
    class Meta:
        model = Meeting
        fields = [
            'title', 'description', 'scheduled_start_time', 'scheduled_end_time',
            'duration_minutes', 'timezone', 'is_recording_enabled',
            'is_waiting_room_enabled', 'is_password_protected', 'max_participants',
            'allow_participants_to_mute', 'allow_participants_to_share_screen',
            'allow_participants_to_record'
        ]

    def validate(self, attrs):
        # Only allow updates if meeting hasn't started
        if self.instance.status == 'in_progress':
            raise serializers.ValidationError("Cannot update meeting that is in progress.")

        # Validate scheduled times
        start_time = attrs.get('scheduled_start_time', self.instance.scheduled_start_time)
        end_time = attrs.get('scheduled_end_time', self.instance.scheduled_end_time)

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time.")

        return attrs


class MeetingInvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for meeting invitations
    """
    meeting_title = serializers.CharField(source='meeting.title', read_only=True)
    meeting_id = serializers.CharField(source='meeting.meeting_id', read_only=True)
    meeting_start_time = serializers.DateTimeField(source='meeting.scheduled_start_time', read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.full_name', read_only=True)

    class Meta:
        model = MeetingInvitation
        fields = [
            'id', 'meeting', 'meeting_title', 'meeting_id', 'meeting_start_time',
            'email', 'invited_by', 'invited_by_name', 'status', 'message',
            'sent_at', 'responded_at'
        ]
        read_only_fields = ['id', 'sent_at', 'responded_at']


class MeetingJoinSerializer(serializers.Serializer):
    """
    Serializer for joining meetings
    """
    meeting_id = serializers.CharField(max_length=12)
    password = serializers.CharField(max_length=10, required=False, allow_blank=True)

    def validate_meeting_id(self, value):
        try:
            meeting = Meeting.objects.get(meeting_id=value)
            if meeting.status == 'cancelled':
                raise serializers.ValidationError("This meeting has been cancelled.")
            return value
        except Meeting.DoesNotExist:
            raise serializers.ValidationError("Meeting not found.")

    def validate(self, attrs):
        meeting_id = attrs.get('meeting_id')
        password = attrs.get('password', '')

        try:
            meeting = Meeting.objects.get(meeting_id=meeting_id)

            # Check password if required
            if meeting.is_password_protected and meeting.meeting_password != password:
                raise serializers.ValidationError("Invalid meeting password.")

            attrs['meeting'] = meeting
            return attrs
        except Meeting.DoesNotExist:
            raise serializers.ValidationError("Meeting not found.")


class MeetingRecordingSerializer(serializers.ModelSerializer):
    """
    Serializer for meeting recordings
    """
    meeting_title = serializers.CharField(source='meeting.title', read_only=True)
    meeting_id = serializers.CharField(source='meeting.meeting_id', read_only=True)
    file_size_mb = serializers.ReadOnlyField()
    duration_formatted = serializers.ReadOnlyField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = MeetingRecording
        fields = [
            'id', 'meeting', 'meeting_title', 'meeting_id', 'title',
            'quality', 'status', 'file_size_bytes', 'file_size_mb',
            'duration_seconds', 'duration_formatted', 'recording_started_at',
            'recording_ended_at', 'processing_completed_at', 'download_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size_bytes', 'duration_seconds', 'recording_started_at',
            'recording_ended_at', 'processing_completed_at', 'created_at', 'updated_at'
        ]

    def get_download_url(self, obj):
        if obj.status == 'ready' and obj.file_path:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/api/meetings/recordings/{obj.id}/download/')
        return None


class MeetingChatSerializer(serializers.ModelSerializer):
    """
    Serializer for meeting chat messages
    """
    participant_name = serializers.CharField(source='participant.user.full_name', read_only=True)
    participant_role = serializers.CharField(source='participant.role', read_only=True)

    class Meta:
        model = MeetingChat
        fields = [
            'id', 'participant', 'participant_name', 'participant_role',
            'message_type', 'content', 'file_name', 'file_size',
            'is_private', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MeetingSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for user meeting settings
    """
    class Meta:
        model = MeetingSettings
        fields = [
            'default_meeting_duration', 'default_max_participants', 'auto_record',
            'auto_mute_participants', 'enable_waiting_room', 'email_meeting_reminders',
            'email_recording_ready', 'email_meeting_invitations', 'default_video_quality',
            'join_with_video_off', 'join_with_audio_muted'
        ]


class InstantMeetingSerializer(serializers.Serializer):
    """
    Serializer for creating instant meetings
    """
    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    is_recording_enabled = serializers.BooleanField(default=True)
    is_password_protected = serializers.BooleanField(default=False)
    max_participants = serializers.IntegerField(default=100, min_value=2, max_value=1000)

    def validate_title(self, value):
        if not value:
            return f"Instant Meeting - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        return value

    def create(self, validated_data):
        request = self.context.get('request')

        # Create instant meeting
        meeting = Meeting.objects.create(
            title=validated_data.get('title', f"Instant Meeting - {timezone.now().strftime('%Y-%m-%d %H:%M')}"),
            description=validated_data.get('description', ''),
            host=request.user,
            meeting_type='instant',
            status='in_progress',
            actual_start_time=timezone.now(),
            is_recording_enabled=validated_data.get('is_recording_enabled', True),
            is_password_protected=validated_data.get('is_password_protected', False),
            max_participants=validated_data.get('max_participants', 100),
            duration_minutes=120  # Default 2 hours for instant meetings
        )

        # Add host as participant
        MeetingParticipant.objects.create(
            meeting=meeting,
            user=request.user,
            role='host',
            status='joined',
            joined_at=timezone.now(),
            can_mute_others=True,
            can_share_screen=True,
            can_record=True
        )

        return meeting


class MeetingStatsSerializer(serializers.Serializer):
    """
    Serializer for meeting statistics
    """
    total_meetings = serializers.IntegerField()
    meetings_this_month = serializers.IntegerField()
    total_participants = serializers.IntegerField()
    total_recording_time = serializers.IntegerField()  # in minutes
    average_meeting_duration = serializers.IntegerField()  # in minutes
    meetings_by_status = serializers.DictField()
    meetings_by_type = serializers.DictField()
    recent_meetings = MeetingListSerializer(many=True)


class ParticipantUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating participant status during meeting
    """
    class Meta:
        model = MeetingParticipant
        fields = [
            'is_audio_muted', 'is_video_disabled', 'is_screen_sharing'
        ]


class MeetingControlSerializer(serializers.Serializer):
    """
    Serializer for meeting control actions
    """
    ACTION_CHOICES = [
        ('start', 'Start Meeting'),
        ('end', 'End Meeting'),
        ('pause_recording', 'Pause Recording'),
        ('resume_recording', 'Resume Recording'),
        ('mute_all', 'Mute All Participants'),
        ('unmute_all', 'Unmute All Participants'),
    ]

    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    participant_id = serializers.UUIDField(required=False)  # For participant-specific actions

    def validate(self, attrs):
        action = attrs.get('action')
        participant_id = attrs.get('participant_id')

        # Some actions require participant_id
        participant_required_actions = ['mute_participant', 'unmute_participant', 'remove_participant']
        if action in participant_required_actions and not participant_id:
            raise serializers.ValidationError(f"participant_id is required for {action} action.")

        return attrs