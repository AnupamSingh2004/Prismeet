from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta
import random
import string
import secrets

from .models import (
    Meeting,
    MeetingParticipant,
    MeetingInvitation,
    WebRTCSession,
    MeetingRecording,
    MeetingAnalytics
)


class MeetingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating meetings
    """
    invitees = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        allow_empty=True,
        write_only=True
    )

    class Meta:
        model = Meeting
        fields = [
            'title', 'description', 'meeting_type', 'scheduled_start',
            'scheduled_end', 'duration_minutes', 'timezone', 'passcode',
            'waiting_room_enabled', 'join_before_host', 'mute_participants_on_join',
            'allow_screen_sharing', 'allow_recording', 'max_participants',
            'invitees'
        ]

    def validate(self, data):
        # Validate scheduled meetings
        if data.get('meeting_type') == 'scheduled':
            if not data.get('scheduled_start'):
                raise serializers.ValidationError("Scheduled meetings must have a start time")

            # Check if scheduled time is in the future
            if data['scheduled_start'] <= timezone.now():
                raise serializers.ValidationError("Scheduled time must be in the future")

        # Set end time if not provided
        if data.get('scheduled_start') and not data.get('scheduled_end'):
            duration = timedelta(minutes=data.get('duration_minutes', 60))
            data['scheduled_end'] = data['scheduled_start'] + duration

        return data

    def create(self, validated_data):
        # Remove invitees from validated_data as it's not a model field
        invitees = validated_data.pop('invitees', [])

        # Generate unique meeting ID
        meeting_id = self.generate_meeting_id()
        validated_data['meeting_id'] = meeting_id

        # Generate passcode if not provided
        if not validated_data.get('passcode'):
            validated_data['passcode'] = self.generate_passcode()

        # Set host information from context
        request = self.context.get('request')
        if request and request.user:
            validated_data['host_id'] = request.user.id
            validated_data['host_email'] = request.user.email
            validated_data['host_name'] = request.user.get_full_name() or request.user.email

        # Set status based on meeting type
        if validated_data.get('meeting_type') == 'instant':
            validated_data['status'] = 'ongoing'
            validated_data['actual_start'] = timezone.now()

        meeting = super().create(validated_data)

        # Add host as participant
        MeetingParticipant.objects.create(
            meeting=meeting,
            user_id=meeting.host_id,
            email=meeting.host_email,
            name=meeting.host_name,
            role='host',
            status='joined' if meeting.status == 'ongoing' else 'invited'
        )

        # Create invitations
        for email in invitees:
            invitation_token = secrets.token_urlsafe(32)
            MeetingInvitation.objects.create(
                meeting=meeting,
                invitee_email=email,
                invitation_token=invitation_token,
                expires_at=timezone.now() + timedelta(days=7)
            )

        return meeting

    def generate_meeting_id(self):
        """Generate unique 9-digit meeting ID"""
        while True:
            meeting_id = ''.join(random.choices(string.digits, k=9))
            if not Meeting.objects.filter(meeting_id=meeting_id).exists():
                return meeting_id

    def generate_passcode(self):
        """Generate 6-digit passcode"""
        return ''.join(random.choices(string.digits, k=6))


class MeetingSerializer(serializers.ModelSerializer):
    """
    Full meeting serializer for responses
    """
    join_url = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()
    is_host = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'description', 'host_id', 'host_email', 'host_name',
            'meeting_id', 'passcode', 'meeting_type', 'scheduled_start',
            'scheduled_end', 'duration_minutes', 'timezone', 'status',
            'actual_start', 'actual_end', 'waiting_room_enabled',
            'join_before_host', 'mute_participants_on_join', 'allow_screen_sharing',
            'allow_recording', 'max_participants', 'participant_count',
            'join_url', 'can_join', 'is_host', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'host_id', 'host_email', 'host_name', 'meeting_id',
            'actual_start', 'actual_end', 'created_at', 'updated_at'
        ]

    def get_join_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/meetings/{obj.meeting_id}/join/')
        return f'/api/meetings/{obj.meeting_id}/join/'

    def get_participant_count(self, obj):
        return obj.participants.filter(status='joined').count()

    def get_can_join(self, obj):
        return obj.can_join()

    def get_is_host(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return str(obj.host_id) == str(request.user.id)
        return False


class MeetingParticipantSerializer(serializers.ModelSerializer):
    """
    Meeting participant serializer
    """
    class Meta:
        model = MeetingParticipant
        fields = [
            'id', 'user_id', 'email', 'name', 'is_guest', 'role', 'status',
            'audio_enabled', 'video_enabled', 'screen_sharing', 'peer_id',
            'joined_at', 'left_at', 'duration_seconds', 'created_at'
        ]
        read_only_fields = [
            'id', 'duration_seconds', 'joined_at', 'left_at', 'created_at'
        ]


class JoinMeetingSerializer(serializers.Serializer):
    """
    Serializer for joining meetings
    """
    passcode = serializers.CharField(max_length=10, required=False)
    name = serializers.CharField(max_length=100, required=False)
    audio_enabled = serializers.BooleanField(default=True)
    video_enabled = serializers.BooleanField(default=True)

    def validate(self, data):
        meeting_id = self.context.get('meeting_id')
        request = self.context.get('request')

        if not meeting_id:
            raise serializers.ValidationError("Meeting ID is required")

        try:
            meeting = Meeting.objects.get(meeting_id=meeting_id)
        except Meeting.DoesNotExist:
            raise serializers.ValidationError("Meeting not found")

        # Check if meeting can be joined
        if not meeting.can_join():
            raise serializers.ValidationError("Meeting cannot be joined at this time")

        # Check passcode if meeting has one
        if meeting.passcode and data.get('passcode') != meeting.passcode:
            raise serializers.ValidationError("Invalid passcode")

        # Check if user is authenticated or provide name for guest
        if not request.user.is_authenticated and not data.get('name'):
            raise serializers.ValidationError("Name is required for guest users")

        # Check participant limit
        current_participants = meeting.participants.filter(status='joined').count()
        if current_participants >= meeting.max_participants:
            raise serializers.ValidationError("Meeting has reached maximum participants")

        self.meeting = meeting
        return data


class WebRTCOfferSerializer(serializers.Serializer):
    """
    Serializer for WebRTC offer/answer exchange
    """
    type = serializers.ChoiceField(choices=['offer', 'answer', 'ice-candidate'])
    sdp = serializers.CharField(required=False, allow_blank=True)
    candidate = serializers.CharField(required=False, allow_blank=True)
    sdpMLineIndex = serializers.IntegerField(required=False)
    sdpMid = serializers.CharField(required=False, allow_blank=True)
    target_peer_id = serializers.CharField(max_length=100)


class MeetingControlSerializer(serializers.Serializer):
    """
    Serializer for meeting controls (mute, video, etc.)
    """
    action = serializers.ChoiceField(choices=[
        'mute_audio', 'unmute_audio', 'enable_video', 'disable_video',
        'start_screen_share', 'stop_screen_share', 'start_recording',
        'stop_recording', 'end_meeting', 'remove_participant'
    ])
    target_participant_id = serializers.UUIDField(required=False)


class MeetingInvitationSerializer(serializers.ModelSerializer):
    """
    Meeting invitation serializer
    """
    meeting_title = serializers.CharField(source='meeting.title', read_only=True)
    meeting_id = serializers.CharField(source='meeting.meeting_id', read_only=True)
    host_name = serializers.CharField(source='meeting.host_name', read_only=True)

    class Meta:
        model = MeetingInvitation
        fields = [
            'id', 'meeting_title', 'meeting_id', 'host_name', 'invitee_email',
            'invitee_name', 'status', 'message', 'sent_at', 'responded_at',
            'expires_at', 'invitation_token'
        ]
        read_only_fields = [
            'id', 'invitation_token', 'sent_at', 'responded_at'
        ]


class CreateInvitationSerializer(serializers.Serializer):
    """
    Serializer for creating meeting invitations
    """
    emails = serializers.ListField(
        child=serializers.EmailField(),
        min_length=1,
        max_length=50
    )
    message = serializers.CharField(max_length=500, required=False, allow_blank=True)


class MeetingRecordingSerializer(serializers.ModelSerializer):
    """
    Meeting recording serializer
    """
    meeting_title = serializers.CharField(source='meeting.title', read_only=True)

    class Meta:
        model = MeetingRecording
        fields = [
            'id', 'recording_id', 'meeting_title', 'status', 'file_size',
            'duration_seconds', 'format', 'started_by_name', 'started_at',
            'ended_at', 'download_url', 'expires_at'
        ]
        read_only_fields = [
            'id', 'recording_id', 'file_size', 'duration_seconds',
            'started_at', 'ended_at', 'download_url'
        ]


class MeetingAnalyticsSerializer(serializers.ModelSerializer):
    """
    Meeting analytics serializer
    """
    meeting_title = serializers.CharField(source='meeting.title', read_only=True)

    class Meta:
        model = MeetingAnalytics
        fields = [
            'meeting_title', 'total_participants', 'max_concurrent_participants',
            'average_duration_seconds', 'total_audio_time_seconds',
            'total_video_time_seconds', 'screen_sharing_duration_seconds',
            'average_connection_quality', 'connection_issues_count',
            'chat_messages_count', 'reactions_count', 'total_bandwidth_mb',
            'peak_bandwidth_mbps', 'created_at', 'updated_at'
        ]
        read_only_fields = '__all__'


class ICEServerConfigSerializer(serializers.Serializer):
    """
    ICE server configuration for WebRTC
    """
    urls = serializers.ListField(
        child=serializers.URLField(),
        help_text="List of STUN/TURN server URLs"
    )
    username = serializers.CharField(required=False, allow_blank=True)
    credential = serializers.CharField(required=False, allow_blank=True)


class WebRTCConfigSerializer(serializers.Serializer):
    """
    WebRTC configuration response
    """
    ice_servers = ICEServerConfigSerializer(many=True)
    peer_id = serializers.CharField()
    room_id = serializers.CharField()
    is_host = serializers.BooleanField()
    media_constraints = serializers.DictField()


class MeetingStatsSerializer(serializers.Serializer):
    """
    Real-time meeting statistics
    """
    meeting_id = serializers.CharField()
    participants_count = serializers.IntegerField()
    duration_seconds = serializers.IntegerField()
    is_recording = serializers.BooleanField()
    bandwidth_usage = serializers.FloatField()
    connection_quality = serializers.FloatField()