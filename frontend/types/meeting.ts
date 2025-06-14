// types/meeting.ts
export interface Meeting {
    id: string;
    meeting_id: string;
    title: string;
    description?: string;
    host: User;
    meeting_type: 'instant' | 'scheduled' | 'recurring';
    status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
    scheduled_start_time?: string;
    scheduled_end_time?: string;
    actual_start_time?: string;
    actual_end_time?: string;
    duration_minutes?: number;
    max_participants?: number;
    is_recording_enabled: boolean;
    is_waiting_room_enabled: boolean;
    passcode?: string;
    created_at: string;
    updated_at: string;
    participants: MeetingParticipant[];
}

export interface MeetingParticipant {
    id: string;
    user: User;
    meeting: string;
    role: 'host' | 'co_host' | 'participant';
    status: 'invited' | 'joined' | 'left' | 'waiting' | 'declined';
    joined_at?: string;
    left_at?: string;
    is_audio_muted: boolean;
    is_video_muted: boolean;
    is_screen_sharing: boolean;
    can_mute_others: boolean;
    can_record: boolean;
}

export interface User {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    profile_picture?: string;
}

export interface MeetingSettings {
    id: string;
    user: string;
    default_audio_muted: boolean;
    default_video_muted: boolean;
    auto_record_meetings: boolean;
    enable_waiting_room: boolean;
    allow_participants_rename: boolean;
    enable_chat: boolean;
    created_at: string;
    updated_at: string;
}

export interface MeetingInvitation {
    id: string;
    meeting: Meeting;
    email: string;
    invited_by: User;
    status: 'pending' | 'accepted' | 'declined';
    sent_at: string;
    responded_at?: string;
}

export interface MeetingChat {
    id: string;
    participant: MeetingParticipant;
    message: string;
    message_type: 'text' | 'system';
    created_at: string;
}

export interface MeetingRecording {
    id: string;
    meeting: Meeting;
    file_path: string;
    file_size: number;
    duration_seconds: number;
    status: 'processing' | 'ready' | 'failed' | 'deleted';
    recording_started_at: string;
    recording_ended_at?: string;
    created_at: string;
}

export interface CreateMeetingRequest {
    title: string;
    description?: string;
    meeting_type: 'instant' | 'scheduled';
    scheduled_start_time?: string;
    scheduled_end_time?: string;
    max_participants?: number;
    is_recording_enabled?: boolean;
    is_waiting_room_enabled?: boolean;
    passcode?: string;
}

export interface JoinMeetingRequest {
    meeting_id: string;
    passcode?: string;
}

export interface MeetingStats {
    total_meetings: number;
    meetings_this_month: number;
    total_participants: number;
    total_recording_time: number;
    average_meeting_duration: number;
    meetings_by_status: Record<string, number>;
    meetings_by_type: Record<string, number>;
    recent_meetings: Meeting[];
}