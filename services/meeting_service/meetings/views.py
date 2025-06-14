from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import uuid
import secrets
import logging

from .models import (
    Meeting, MeetingParticipant, MeetingInvitation,
    WebRTCSession, MeetingRecording, MeetingAnalytics
)
from .serializers import (
    MeetingCreateSerializer, MeetingSerializer, MeetingParticipantSerializer,
    JoinMeetingSerializer, WebRTCOfferSerializer, MeetingControlSerializer,
    MeetingInvitationSerializer, CreateInvitationSerializer,
    MeetingRecordingSerializer, WebRTCConfigSerializer, MeetingStatsSerializer
)
from .utils import get_ice_servers, generate_peer_id
from .authentication import OptionalAuthentication

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


class MeetingViewSet(viewsets.ModelViewSet):
    """
    Meeting management ViewSet
    """
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Meeting.objects.filter(host_id=self.request.user.id)

    def get_serializer_class(self):
        if self.action == 'create':
            return MeetingCreateSerializer
        return MeetingSerializer

    def create(self, request, *args, **kwargs):
        """Create a new meeting"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        meeting = serializer.save()

        # Create analytics record
        MeetingAnalytics.objects.create(meeting=meeting)

        response_serializer = MeetingSerializer(meeting, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a scheduled meeting"""
        meeting = self.get_object()

        if meeting.status != 'scheduled':
            return Response(
                {'error': 'Only scheduled meetings can be started'},
                status=status.HTTP_400_BAD_REQUEST
            )

        meeting.status = 'ongoing'
        meeting.actual_start = timezone.now()
        meeting.save()

        # Notify all participants
        self.notify_meeting_status_change(meeting, 'started')

        serializer = self.get_serializer(meeting)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a meeting"""
        meeting = self.get_object()

        if meeting.status != 'ongoing':
            return Response(
                {'error': 'Only ongoing meetings can be ended'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            meeting.status = 'ended'
            meeting.actual_end = timezone.now()
            meeting.save()

            # Update all joined participants to left
            meeting.participants.filter(status='joined').update(
                status='left',
                left_at=timezone.now()
            )

            # Update analytics
            self.update_meeting_analytics(meeting)

        # Notify all participants
        self.notify_meeting_status_change(meeting, 'ended')

        serializer = self.get_serializer(meeting)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """Get meeting participants"""
        meeting = self.get_object()
        participants = meeting.participants.all()
        serializer = MeetingParticipantSerializer(participants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Send meeting invitations"""
        meeting = self.get_object()
        serializer = CreateInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        emails = serializer.validated_data['emails']
        message = serializer.validated_data.get('message', '')

        invitations = []
        for email in emails:
            invitation, created = MeetingInvitation.objects.get_or_create(
                meeting=meeting,
                invitee_email=email,
                defaults={
                    'invitation_token': secrets.token_urlsafe(32),
                    'message': message,
                    'expires_at': timezone.now() + timezone.timedelta(days=7)
                }
            )
            if created:
                invitations.append(invitation)

        # TODO: Send email invitations

        response_serializer = MeetingInvitationSerializer(invitations, many=True)
        return Response(response_serializer.data)

    def notify_meeting_status_change(self, meeting, action):
        """Notify participants about meeting status changes"""
        async_to_sync(channel_layer.group_send)(
            f'meeting_{meeting.meeting_id}',
            {
                'type': 'meeting_status_change',
                'meeting_id': meeting.meeting_id,
                'action': action,
                'timestamp': timezone.now().isoformat()
            }
        )

    def update_meeting_analytics(self, meeting):
        """Update meeting analytics after meeting ends"""
        try:
            analytics = meeting.analytics
            participants = meeting.participants.all()

            analytics.total_participants = participants.count()
            analytics.max_concurrent_participants = participants.filter(status='joined').count()

            # Calculate average duration
            durations = [p.duration_seconds for p in participants if p.duration_seconds > 0]
            if durations:
                analytics.average_duration_seconds = sum(durations) // len(durations)

            analytics.save()
        except Exception as e:
            logger.error(f"Failed to update analytics for meeting {meeting.id}: {e}")


class JoinMeetingView(APIView):
    """
    Handle meeting join requests for both authenticated and guest users
    """
    authentication_classes = [OptionalAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, meeting_id):
        try:
            meeting = Meeting.objects.get(meeting_id=meeting_id)

            if not meeting.can_join():
                return Response(
                    {'error': 'Meeting is not available for joining'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Handle authenticated users
            if request.user and hasattr(request.user, 'is_authenticated') and request.user.is_authenticated:
                participant_data = {
                    'meeting': meeting,
                    'user_id': request.user.id,
                    'email': request.user.email,
                    'name': request.user.get_full_name() or request.user.email,
                    'is_guest': False,
                    'role': 'host' if str(request.user.id) == str(meeting.host_id) else 'participant'
                }
            else:
                # Handle guest users
                name = request.data.get('name')
                email = request.data.get('email', '')

                if not name:
                    return Response(
                        {'error': 'Name is required for guest users'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                participant_data = {
                    'meeting': meeting,
                    'user_id': None,
                    'email': email,
                    'name': name,
                    'is_guest': True,
                    'role': 'participant'
                }

            # Create or update participant
            participant, created = MeetingParticipant.objects.get_or_create(
                meeting=meeting,
                user_id=participant_data['user_id'],
                email=participant_data['email'] if participant_data['is_guest'] else None,
                defaults=participant_data
            )

            if not created:
                # Update existing participant
                for key, value in participant_data.items():
                    if key != 'meeting':
                        setattr(participant, key, value)
                participant.save()

            participant.join_meeting()

            serializer = MeetingParticipantSerializer(participant)
            return Response({
                'participant': serializer.data,
                'meeting': MeetingSerializer(meeting).data,
                'join_url': meeting.get_join_url()
            })

        except Meeting.DoesNotExist:
            return Response(
                {'error': 'Meeting not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LeaveMeetingView(APIView):
    """
    Handle leaving meeting
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, meeting_id, participant_id):
        """Leave a meeting"""
        meeting = get_object_or_404(Meeting, meeting_id=meeting_id)
        participant = get_object_or_404(
            MeetingParticipant,
            id=participant_id,
            meeting=meeting
        )

        participant.leave_meeting()

        # Notify other participants
        async_to_sync(channel_layer.group_send)(
            f'meeting_{meeting.meeting_id}',
            {
                'type': 'participant_left',
                'participant_id': str(participant.id),
                'meeting_id': meeting.meeting_id
            }
        )

        return Response({'message': 'Left meeting successfully'})


class WebRTCSignalingView(APIView):
    """
    Handle WebRTC signaling (offer/answer/ice-candidates)
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, meeting_id):
        """Handle WebRTC signaling messages"""
        serializer = WebRTCOfferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        meeting = get_object_or_404(Meeting, meeting_id=meeting_id)

        # Forward signaling message to target peer
        async_to_sync(channel_layer.group_send)(
            f'meeting_{meeting_id}',
            {
                'type': 'webrtc_signaling',
                'signaling_data': serializer.validated_data,
                'meeting_id': meeting_id
            }
        )

        return Response({'message': 'Signaling message sent'})


class MeetingControlView(APIView):
    """
    Handle meeting controls (mute, video, screen share, etc.)
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, meeting_id):
        """Execute meeting control actions"""
        serializer = MeetingControlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        meeting = get_object_or_404(Meeting, meeting_id=meeting_id)
        action = serializer.validated_data['action']
        target_participant_id = serializer.validated_data.get('target_participant_id')

        # Get current participant
        participant = None
        if request.user.is_authenticated:
            participant = meeting.participants.filter(user_id=request.user.id).first()

        if not participant:
            return Response(
                {'error': 'Participant not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Handle different actions
        if action in ['mute_audio', 'unmute_audio']:
            participant.audio_enabled = action == 'unmute_audio'
            participant.save()

        elif action in ['enable_video', 'disable_video']:
            participant.video_enabled = action == 'enable_video'
            participant.save()

        elif action in ['start_screen_share', 'stop_screen_share']:
            participant.screen_sharing = action == 'start_screen_share'
            participant.save()

        elif action == 'start_recording':
            if participant.role not in ['host', 'co_host']:
                return Response(
                    {'error': 'Only hosts can start recording'},
                    status=status.HTTP_403_FORBIDDEN
                )
            # TODO: Implement recording logic

        elif action == 'end_meeting':
            if participant.role != 'host':
                return Response(
                    {'error': 'Only host can end meeting'},
                    status=status.HTTP_403_FORBIDDEN
                )
            meeting.status = 'ended'
            meeting.actual_end = timezone.now()
            meeting.save()

        # Notify participants about the control action
        async_to_sync(channel_layer.group_send)(
            f'meeting_{meeting_id}',
            {
                'type': 'meeting_control',
                'action': action,
                'participant_id': str(participant.id),
                'target_participant_id': str(target_participant_id) if target_participant_id else None,
                'meeting_id': meeting_id
            }
        )

        return Response({
            'message': f'Action {action} executed successfully',
            'participant': MeetingParticipantSerializer(participant).data
        })


class MeetingStatsView(APIView):
    """
    Get real-time meeting statistics
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, meeting_id):
        """Get meeting statistics"""
        meeting = get_object_or_404(Meeting, meeting_id=meeting_id)

        participants_count = meeting.participants.filter(status='joined').count()
        duration_seconds = 0

        if meeting.actual_start:
            end_time = meeting.actual_end or timezone.now()
            duration_seconds = int((end_time - meeting.actual_start).total_seconds())

        is_recording = meeting.recordings.filter(status='recording').exists()

        stats = {
            'meeting_id': meeting_id,
            'participants_count': participants_count,
            'duration_seconds': duration_seconds,
            'is_recording': is_recording,
            'bandwidth_usage': 0.0,  # TODO: Implement bandwidth tracking
            'connection_quality': 0.0  # TODO: Implement connection quality tracking
        }

        serializer = MeetingStatsSerializer(stats)
        return Response(serializer.data)


class PublicMeetingView(APIView):
    """
    Get public meeting info for join page
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, meeting_id):
        """Get public meeting information"""
        meeting = get_object_or_404(Meeting, meeting_id=meeting_id)

        # Return limited public information
        data = {
            'meeting_id': meeting.meeting_id,
            'title': meeting.title,
            'host_name': meeting.host_name,
            'status': meeting.status,
            'scheduled_start': meeting.scheduled_start,
            'waiting_room_enabled': meeting.waiting_room_enabled,
            'passcode_required': bool(meeting.passcode),
            'can_join': meeting.can_join(),
            'participant_count': meeting.participants.filter(status='joined').count(),
            'max_participants': meeting.max_participants
        }

        return Response(data)