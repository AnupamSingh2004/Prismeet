from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from django.http import Http404, HttpResponse
from django.core.exceptions import PermissionDenied
from .models import (
    Meeting, MeetingParticipant, MeetingInvitation,
    MeetingRecording, MeetingChat, MeetingSettings
)
from .serializers import (
    MeetingListSerializer, MeetingDetailSerializer, MeetingCreateSerializer,
    MeetingUpdateSerializer, MeetingParticipantSerializer, MeetingInvitationSerializer,
    MeetingJoinSerializer, MeetingRecordingSerializer, MeetingChatSerializer,
    MeetingSettingsSerializer, InstantMeetingSerializer, MeetingStatsSerializer,
    ParticipantUpdateSerializer, MeetingControlSerializer
)
import logging

logger = logging.getLogger(__name__)


class MeetingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing meetings
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return MeetingListSerializer
        elif self.action == 'create':
            return MeetingCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MeetingUpdateSerializer
        elif self.action == 'join':
            return MeetingJoinSerializer
        elif self.action == 'instant':
            return InstantMeetingSerializer
        elif self.action == 'stats':
            return MeetingStatsSerializer
        elif self.action == 'control':
            return MeetingControlSerializer
        return MeetingDetailSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Meeting.objects.filter(
            Q(host=user) | Q(participants__user=user)
        ).distinct().select_related('host').prefetch_related('participants__user')

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by type
        type_filter = self.request.query_params.get('type')
        if type_filter:
            queryset = queryset.filter(meeting_type=type_filter)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(scheduled_start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(scheduled_start_time__lte=end_date)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        # Only allow host to update
        if self.get_object().host != self.request.user:
            raise PermissionDenied("Only the meeting host can update the meeting.")
        serializer.save()

    def perform_destroy(self, instance):
        # Only allow host to delete
        if instance.host != self.request.user:
            raise PermissionDenied("Only the meeting host can delete the meeting.")

        # Can only delete if meeting hasn't started
        if instance.status == 'in_progress':
            raise PermissionDenied("Cannot delete meeting that is in progress.")

        instance.status = 'cancelled'
        instance.save()

    @action(detail=False, methods=['post'])
    def instant(self, request):
        """
        Create and start an instant meeting
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meeting = serializer.save()

        response_serializer = MeetingDetailSerializer(meeting, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def join(self, request):
        """
        Join a meeting by meeting ID
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        meeting = serializer.validated_data['meeting']
        user = request.user

        # Check if user can join
        if not meeting.can_join(user):
            # Create participant if not exists
            participant, created = MeetingParticipant.objects.get_or_create(
                meeting=meeting,
                user=user,
                defaults={
                    'role': 'participant',
                    'status': 'invited'
                }
            )
        else:
            participant = MeetingParticipant.objects.get(meeting=meeting, user=user)

        # Check waiting room
        if meeting.is_waiting_room_enabled and participant.role != 'host':
            participant.status = 'waiting'
            participant.save()
            return Response({
                'message': 'You are in the waiting room. Please wait for the host to admit you.',
                'status': 'waiting',
                'meeting': MeetingDetailSerializer(meeting, context={'request': request}).data
            })

        # Join the meeting
        participant.join_meeting()

        # Start meeting if host joins
        if participant.role == 'host' and meeting.status == 'scheduled':
            meeting.start_meeting()

        response_data = MeetingDetailSerializer(meeting, context={'request': request}).data
        return Response({
            'message': 'Successfully joined the meeting',
            'meeting': response_data
        })

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """
        Leave a meeting
        """
        meeting = self.get_object()
        user = request.user

        try:
            participant = MeetingParticipant.objects.get(meeting=meeting, user=user)
            participant.leave_meeting()

            # End meeting if host leaves and no other hosts
            if participant.role == 'host':
                other_hosts = meeting.participants.filter(
                    role__in=['host', 'co_host'],
                    status='joined'
                ).exclude(user=user).exists()

                if not other_hosts:
                    meeting.end_meeting()

            return Response({'message': 'Successfully left the meeting'})
        except MeetingParticipant.DoesNotExist:
            return Response(
                {'error': 'You are not a participant in this meeting'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def control(self, request, pk=None):
        """
        Control meeting (start, end, mute all, etc.)
        """
        meeting = self.get_object()
        user = request.user

        # Check if user is host or co-host
        try:
            participant = MeetingParticipant.objects.get(meeting=meeting, user=user)
            if participant.role not in ['host', 'co_host']:
                raise PermissionDenied("Only hosts can control the meeting.")
        except MeetingParticipant.DoesNotExist:
            raise PermissionDenied("You are not a participant in this meeting.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data['action']

        if action_type == 'start':
            meeting.start_meeting()
            message = 'Meeting started'
        elif action_type == 'end':
            meeting.end_meeting()
            message = 'Meeting ended'
        elif action_type == 'mute_all':
            meeting.participants.filter(status='joined').update(is_audio_muted=True)
            message = 'All participants muted'
        elif action_type == 'unmute_all':
            meeting.participants.filter(status='joined').update(is_audio_muted=False)
            message = 'All participants unmuted'
        else:
            return Response(
                {'error': 'Invalid action'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({'message': message})

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """
        Get meeting participants
        """
        meeting = self.get_object()
        participants = meeting.participants.all().select_related('user')
        serializer = MeetingParticipantSerializer(participants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """
        Invite participants to meeting
        """
        meeting = self.get_object()

        # Check if user is host
        if meeting.host != request.user:
            raise PermissionDenied("Only the meeting host can send invitations.")

        emails = request.data.get('emails', [])
        if not emails:
            return Response(
                {'error': 'Email list is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        invitations_sent = []
        for email in emails:
            invitation, created = MeetingInvitation.objects.get_or_create(
                meeting=meeting,
                email=email,
                defaults={'invited_by': request.user}
            )
            if created:
                invitations_sent.append(email)
                # TODO: Send email invitation
                logger.info(f"Invitation sent to {email} for meeting {meeting.meeting_id}")

        return Response({
            'message': f'Invitations sent to {len(invitations_sent)} participants',
            'invited': invitations_sent
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get meeting statistics for the user
        """
        user = request.user

        # Get user's meetings
        user_meetings = Meeting.objects.filter(
            Q(host=user) | Q(participants__user=user)
        ).distinct()

        # Calculate stats
        total_meetings = user_meetings.count()
        meetings_this_month = user_meetings.filter(
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year
        ).count()

        # Get completed meetings for duration stats
        completed_meetings = user_meetings.filter(status='completed')
        total_participants = MeetingParticipant.objects.filter(
            meeting__in=user_meetings
        ).count()

        # Calculate recording time and average duration
        recordings = MeetingRecording.objects.filter(meeting__in=user_meetings, status='ready')
        total_recording_time = recordings.aggregate(
            total=Sum('duration_seconds')
        )['total'] or 0
        total_recording_time = total_recording_time // 60  # Convert to minutes

        avg_duration = completed_meetings.filter(
            actual_start_time__isnull=False,
            actual_end_time__isnull=False
        ).aggregate(
            avg=Avg('duration_minutes')
        )['avg'] or 0

        # Meetings by status
        meetings_by_status = dict(
            user_meetings.values('status').annotate(count=Count('id')).values_list('status', 'count')
        )

        # Meetings by type
        meetings_by_type = dict(
            user_meetings.values('meeting_type').annotate(count=Count('id')).values_list('meeting_type', 'count')
        )

        # Recent meetings
        recent_meetings = user_meetings.order_by('-created_at')[:5]

        stats_data = {
            'total_meetings': total_meetings,
            'meetings_this_month': meetings_this_month,
            'total_participants': total_participants,
            'total_recording_time': int(total_recording_time),
            'average_meeting_duration': int(avg_duration),
            'meetings_by_status': meetings_by_status,
            'meetings_by_type': meetings_by_type,
            'recent_meetings': MeetingListSerializer(recent_meetings, many=True, context={'request': request}).data
        }

        serializer = self.get_serializer(stats_data)
        return Response(serializer.data)


class MeetingParticipantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing meeting participants
    """
    serializer_class = MeetingParticipantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        meeting_id = self.kwargs.get('meeting_pk')
        if meeting_id:
            return MeetingParticipant.objects.filter(
                meeting_id=meeting_id
            ).select_related('user', 'meeting')
        return MeetingParticipant.objects.none()

    @action(detail=True, methods=['patch'])
    def update_status(self, request, meeting_pk=None, pk=None):
        """
        Update participant audio/video status
        """
        participant = self.get_object()

        # Only allow self-updates or host updates
        if participant.user != request.user:
            try:
                meeting_participant = MeetingParticipant.objects.get(
                    meeting_id=meeting_pk,
                    user=request.user
                )
                if meeting_participant.role not in ['host', 'co_host']:
                    raise PermissionDenied("Insufficient permissions")
            except MeetingParticipant.DoesNotExist:
                raise PermissionDenied("You are not a participant in this meeting")

        serializer = ParticipantUpdateSerializer(participant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def promote(self, request, meeting_pk=None, pk=None):
        """
        Promote participant to co-host
        """
        participant = self.get_object()
        meeting = participant.meeting

        # Check if requester is host
        if meeting.host != request.user:
            raise PermissionDenied("Only the meeting host can promote participants")

        participant.role = 'co_host'
        participant.can_mute_others = True
        participant.can_record = True
        participant.save()

        return Response({'message': 'Participant promoted to co-host'})

    @action(detail=True, methods=['post'])
    def remove(self, request, meeting_pk=None, pk=None):
        """
        Remove participant from meeting
        """
        participant = self.get_object()
        meeting = participant.meeting

        # Check if requester is host
        if meeting.host != request.user:
            raise PermissionDenied("Only the meeting host can remove participants")

        if participant.role == 'host':
            return Response(
                {'error': 'Cannot remove the meeting host'},
                status=status.HTTP_400_BAD_REQUEST
            )

        participant.leave_meeting()
        return Response({'message': 'Participant removed from meeting'})


class MeetingRecordingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing meeting recordings
    """
    serializer_class = MeetingRecordingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return MeetingRecording.objects.filter(
            Q(meeting__host=user) | Q(meeting__participants__user=user)
        ).distinct().select_related('meeting').order_by('-recording_started_at')

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download recording file
        """
        recording = self.get_object()

        if recording.status != 'ready':
            return Response(
                {'error': 'Recording is not ready for download'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # TODO: Implement file download logic
        # This should serve the actual file from storage
        return Response({'download_url': f'/media/recordings/{recording.file_path}'})

    @action(detail=True, methods=['delete'])
    def delete_recording(self, request, pk=None):
        """
        Delete a recording
        """
        recording = self.get_object()

        # Only allow meeting host to delete recordings
        if recording.meeting.host != request.user:
            raise PermissionDenied("Only the meeting host can delete recordings")

        recording.status = 'deleted'
        recording.save()

        # TODO: Delete actual file from storage

        return Response({'message': 'Recording deleted successfully'})


class MeetingChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for meeting chat messages
    """
    serializer_class = MeetingChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        meeting_id = self.kwargs.get('meeting_pk')
        if meeting_id:
            # Check if user is participant
            try:
                MeetingParticipant.objects.get(
                    meeting_id=meeting_id,
                    user=self.request.user
                )
                return MeetingChat.objects.filter(
                    meeting_id=meeting_id
                ).select_related('participant__user').order_by('created_at')
            except MeetingParticipant.DoesNotExist:
                raise PermissionDenied("You are not a participant in this meeting")
        return MeetingChat.objects.none()

    def perform_create(self, serializer):
        meeting_id = self.kwargs.get('meeting_pk')
        try:
            participant = MeetingParticipant.objects.get(
                meeting_id=meeting_id,
                user=self.request.user
            )
            serializer.save(participant=participant)
        except MeetingParticipant.DoesNotExist:
            raise PermissionDenied("You are not a participant in this meeting")


class MeetingSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user meeting settings
    """
    serializer_class = MeetingSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MeetingSettings.objects.filter(user=self.request.user)

    def get_object(self):
        settings, created = MeetingSettings.objects.get_or_create(
            user=self.request.user
        )
        return settings

    def list(self, request, *args, **kwargs):
        """
        Return user's meeting settings
        """
        settings = self.get_object()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Update user's meeting settings
        """
        settings = self.get_object()
        serializer = self.get_serializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MeetingInvitationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for meeting invitations
    """
    serializer_class = MeetingInvitationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MeetingInvitation.objects.filter(
            email=self.request.user.email
        ).select_related('meeting', 'invited_by').order_by('-sent_at')

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """
        Accept meeting invitation
        """
        invitation = self.get_object()

        if invitation.status != 'pending':
            return Response(
                {'error': 'Invitation has already been responded to'},
                status=status.HTTP_400_BAD_REQUEST
            )

        invitation.accept()

        # Add user as participant
        MeetingParticipant.objects.get_or_create(
            meeting=invitation.meeting,
            user=request.user,
            defaults={'role': 'participant'}
        )

        return Response({'message': 'Invitation accepted'})

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """
        Decline meeting invitation
        """
        invitation = self.get_object()

        if invitation.status != 'pending':
            return Response(
                {'error': 'Invitation has already been responded to'},
                status=status.HTTP_400_BAD_REQUEST
            )

        invitation.decline()
        return Response({'message': 'Invitation declined'})