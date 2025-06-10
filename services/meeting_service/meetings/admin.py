from django.contrib import admin
from .models import (
    Meeting, MeetingParticipant, MeetingInvitation,
    MeetingRecording, MeetingChat, MeetingSettings
)

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'meeting_id', 'host', 'status', 'meeting_type', 'created_at']
    list_filter = ['status', 'meeting_type', 'created_at']
    search_fields = ['title', 'meeting_id', 'host__email']
    readonly_fields = ['meeting_id', 'created_at', 'updated_at']

@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'meeting', 'role', 'status', 'joined_at']
    list_filter = ['role', 'status', 'joined_at']
    search_fields = ['user__email', 'meeting__title']

@admin.register(MeetingRecording)
class MeetingRecordingAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'title', 'quality', 'status', 'file_size_mb', 'duration_formatted']
    list_filter = ['status', 'quality', 'recording_started_at']
    search_fields = ['meeting__title', 'title']