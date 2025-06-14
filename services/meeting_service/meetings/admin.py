from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Meeting, MeetingParticipant, MeetingInvitation,
    WebRTCSession, MeetingRecording, MeetingAnalytics
)


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'meeting_id', 'host_name', 'meeting_type',
        'status', 'participant_count', 'scheduled_start', 'created_at'
    ]
    list_filter = ['status', 'meeting_type', 'created_at', 'scheduled_start']
    search_fields = ['title', 'meeting_id', 'host_email', 'host_name']
    readonly_fields = ['meeting_id', 'actual_start', 'actual_end', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'meeting_id', 'meeting_type')
        }),
        ('Host Information', {
            'fields': ('host_id', 'host_email', 'host_name')
        }),
        ('Schedule', {
            'fields': ('scheduled_start', 'scheduled_end', 'duration_minutes', 'timezone')
        }),
        ('Status', {
            'fields': ('status', 'actual_start', 'actual_end')
        }),
        ('Security', {
            'fields': ('passcode', 'waiting_room_enabled', 'join_before_host')
        }),
        ('Settings', {
            'fields': (
                'mute_participants_on_join', 'allow_screen_sharing',
                'allow_recording', 'max_participants'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Participants'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('participants')


@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'meeting_title', 'email', 'role', 'status',
        'is_guest', 'joined_at', 'duration_display'
    ]
    list_filter = ['role', 'status', 'is_guest', 'joined_at']
    search_fields = ['name', 'email', 'meeting__title']
    readonly_fields = ['joined_at', 'left_at', 'duration_seconds', 'created_at', 'updated_at']

    fieldsets = (
        ('Participant Information', {
            'fields': ('name', 'email', 'user_id', 'is_guest')
        }),
        ('Meeting Details', {
            'fields': ('meeting', 'role', 'status')
        }),
        ('Media Status', {
            'fields': ('audio_enabled', 'video_enabled', 'screen_sharing')
        }),
        ('Connection Details', {
            'fields': ('peer_id', 'socket_id', 'ip_address', 'user_agent')
        }),
        ('Timing', {
            'fields': ('joined_at', 'left_at', 'duration_seconds')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def meeting_title(self, obj):
        return obj.meeting.title
    meeting_title.short_description = 'Meeting'

    def duration_display(self, obj):
        if obj.duration_seconds:
            minutes = obj.duration_seconds // 60
            seconds = obj.duration_seconds % 60
            return f"{minutes}m {seconds}s"
        return "-"
    duration_display.short_description = 'Duration'


@admin.register(MeetingInvitation)
class MeetingInvitationAdmin(admin.ModelAdmin):
    list_display = [
        'invitee_email', 'meeting_title', 'status',
        'sent_at', 'responded_at', 'expires_at'
    ]
    list_filter = ['status', 'sent_at', 'expires_at']
    search_fields = ['invitee_email', 'meeting__title']
    readonly_fields = ['invitation_token', 'sent_at', 'responded_at']

    fieldsets = (
        ('Invitation Details', {
            'fields': ('meeting', 'invitee_email', 'invitee_name', 'message')
        }),
        ('Status', {
            'fields': ('status', 'invitation_token')
        }),
        ('Timing', {
            'fields': ('sent_at', 'responded_at', 'expires_at')
        })
    )

    def meeting_title(self, obj):
        return obj.meeting.title
    meeting_title.short_description = 'Meeting'


@admin.register(WebRTCSession)
class WebRTCSessionAdmin(admin.ModelAdmin):
    list_display = [
        'session_id', 'participant_name', 'meeting_title',
        'status', 'connection_state', 'started_at', 'ended_at'
    ]
    list_filter = ['status', 'connection_state', 'started_at']
    search_fields = ['session_id', 'participant__name', 'meeting__title']
    readonly_fields = ['started_at', 'ended_at', 'last_updated']

    fieldsets = (
        ('Session Information', {
            'fields': ('meeting', 'participant', 'peer_id', 'session_id')
        }),
        ('Connection Status', {
            'fields': ('status', 'connection_state', 'ice_connection_state')
        }),
        ('Configuration', {
            'fields': ('ice_servers', 'local_tracks', 'remote_tracks')
        }),
        ('Statistics', {
            'fields': ('stats_data',)
        }),
        ('Timing', {
            'fields': ('started_at', 'ended_at', 'last_updated')
        })
    )

    def participant_name(self, obj):
        return obj.participant.name
    participant_name.short_description = 'Participant'

    def meeting_title(self, obj):
        return obj.meeting.title
    meeting_title.short_description = 'Meeting'


@admin.register(MeetingRecording)
class MeetingRecordingAdmin(admin.ModelAdmin):
    list_display = [
        'recording_id', 'meeting_title', 'status',
        'duration_display', 'file_size_display', 'started_at'
    ]
    list_filter = ['status', 'format', 'started_at']
    search_fields = ['recording_id', 'meeting__title']
    readonly_fields = ['recording_id', 'started_at', 'ended_at', 'file_size', 'duration_seconds']

    fieldsets = (
        ('Recording Information', {
            'fields': ('meeting', 'recording_id', 'status', 'format')
        }),
        ('File Details', {
            'fields': ('file_path', 'file_size', 'duration_seconds')
        }),
        ('Metadata', {
            'fields': ('started_by', 'started_by_name')
        }),
        ('Processing', {
            'fields': ('processing_status', 'download_url', 'expires_at')
        }),
        ('Timing', {
            'fields': ('started_at', 'ended_at')
        })
    )

    def meeting_title(self, obj):
        return obj.meeting.title
    meeting_title.short_description = 'Meeting'

    def duration_display(self, obj):
        if obj.duration_seconds:
            minutes = obj.duration_seconds // 60
            seconds = obj.duration_seconds % 60
            return f"{minutes}m {seconds}s"
        return "-"
    duration_display.short_description = 'Duration'

    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size > 1024 * 1024 * 1024:
                return f"{obj.file_size / (1024 * 1024 * 1024):.1f} GB"
            elif obj.file_size > 1024 * 1024:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
            else:
                return f"{obj.file_size / 1024:.1f} KB"
        return "-"
    file_size_display.short_description = 'File Size'


@admin.register(MeetingAnalytics)
class MeetingAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'meeting_title', 'total_participants', 'max_concurrent_participants',
        'average_duration_display', 'total_bandwidth_display', 'created_at'
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['meeting__title']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Meeting Information', {
            'fields': ('meeting',)
        }),
        ('Participation Metrics', {
            'fields': (
                'total_participants', 'max_concurrent_participants',
                'average_duration_seconds'
            )
        }),
        ('Media Metrics', {
            'fields': (
                'total_audio_time_seconds', 'total_video_time_seconds',
                'screen_sharing_duration_seconds'
            )
        }),
        ('Quality Metrics', {
            'fields': ('average_connection_quality', 'connection_issues_count')
        }),
        ('Engagement Metrics', {
            'fields': ('chat_messages_count', 'reactions_count')
        }),
        ('Technical Metrics', {
            'fields': ('total_bandwidth_mb', 'peak_bandwidth_mbps')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )

    def meeting_title(self, obj):
        return obj.meeting.title
    meeting_title.short_description = 'Meeting'

    def average_duration_display(self, obj):
        if obj.average_duration_seconds:
            minutes = obj.average_duration_seconds // 60
            seconds = obj.average_duration_seconds % 60
            return f"{minutes}m {seconds}s"
        return "-"
    average_duration_display.short_description = 'Avg Duration'

    def total_bandwidth_display(self, obj):
        if obj.total_bandwidth_mb:
            return f"{obj.total_bandwidth_mb:.1f} MB"
        return "-"
    total_bandwidth_display.short_description = 'Total Bandwidth'