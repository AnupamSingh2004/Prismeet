// src/lib/auth.ts
import api from './api';
import Cookies from 'js-cookie';
import { LoginRequest, RegisterRequest, AuthResponse, User } from '@/types/auth';

export class AuthService {
    static async login(data: LoginRequest): Promise<AuthResponse> {
        const response = await api.post('/login/', data);
        const { user, token } = response.data;

        Cookies.set('auth_token', token, { expires: 7 });
        Cookies.set('user', JSON.stringify(user), { expires: 7 });

        return response.data;
    }

    static async register(data: RegisterRequest): Promise<AuthResponse> {
        const response = await api.post('/register/', data);
        return response.data;
    }

    static async logout(): Promise<void> {
        try {
            await api.post('/logout/');
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            Cookies.remove('auth_token');
            Cookies.remove('user');
        }
    }

    static async getProfile(): Promise<User> {
        const response = await api.get('/profile/');
        return response.data;
    }

    static async updateProfile(data: Partial<User>): Promise<User> {
        const response = await api.put('/profile/', data);
        Cookies.set('user', JSON.stringify(response.data), { expires: 7 });
        return response.data;
    }

    static async changePassword(data: {
        old_password: string;
        new_password: string;
        confirm_password: string;
    }): Promise<void> {
        await api.post('/change-password/', data);
    }

    static async requestPasswordReset(email: string): Promise<void> {
        await api.post('/password-reset-request/', { email });
    }

    static async confirmPasswordReset(data: {
        token: string;
        new_password: string;
        confirm_password: string;
    }): Promise<void> {
        await api.post('/password-reset-confirm/', data);
    }

    static async verifyEmail(token: string): Promise<void> {
        await api.post('/verify-email/', { token });
    }

    static async resendVerificationEmail(): Promise<void> {
        await api.post('/resend-verification/');
    }

    static getCurrentUser(): User | null {
        const userCookie = Cookies.get('user');
        return userCookie ? JSON.parse(userCookie) : null;
    }

    static isAuthenticated(): boolean {
        return !!Cookies.get('auth_token');
    }
}