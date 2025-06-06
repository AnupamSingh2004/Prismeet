export interface User {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    full_name: string;
    profile_picture?: string;
    phone_number?: string;
    timezone?: string;
    default_meeting_duration?: number;
    is_email_verified: boolean;
    provider: string;
    created_at: string;
    last_login_at?: string;
    profile?: {
        bio?: string;
        company?: string;
        job_title?: string;
        website?: string;
        email_notifications: boolean;
        meeting_reminders: boolean;
        recording_notifications: boolean;
    };
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    email: string;
    first_name: string;
    last_name: string;
    password: string;
    confirm_password: string;
    phone_number?: string;
}

export interface AuthResponse {
    user: User;
    token: string;
    message: string;
}

export interface ApiError {
    detail?: string;
    error?: string;
    non_field_errors?: string[];
    [key: string]: any;
}