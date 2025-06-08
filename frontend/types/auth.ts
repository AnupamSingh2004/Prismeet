// types/auth.ts
import { User } from './user';

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

// Re-export User for convenience
export type { User };