import { User } from '@/types/auth';

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface RegisterData {
    email: string;
    password: string;
    confirm_password: string;
    first_name: string;
    last_name: string;
    phone_number?: string;
}

export interface AuthResponse {
    user: User;
    token: string;
    message: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class AuthService {
    private static TOKEN_KEY = 'authToken';
    private static USER_KEY = 'currentUser';

    static async login(credentials: LoginCredentials): Promise<AuthResponse> {
        const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(credentials),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Login failed');
        }

        const data = await response.json();
        this.storeAuthData(data.token, data.user);
        return data;
    }

    static async register(userData: RegisterData): Promise<AuthResponse> {
        const response = await fetch(`${API_BASE_URL}/api/auth/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Registration failed');
        }

        const data = await response.json();
        this.storeAuthData(data.token, data.user);
        return data;
    }

    // Send Google token to Django backend for processing
    static async googleAuth(googleToken: string): Promise<AuthResponse> {
        const response = await fetch(`${API_BASE_URL}/api/auth/google-auth/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ google_token: googleToken }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Google authentication failed');
        }

        const data = await response.json();
        this.storeAuthData(data.token, data.user);
        return data;
    }

    static async logout(): Promise<void> {
        const token = this.getToken();
        if (token) {
            try {
                await fetch(`${API_BASE_URL}/api/auth/logout/`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Token ${token}`,
                        'Content-Type': 'application/json',
                    },
                });
            } catch (error) {
                console.error('Logout API call failed:', error);
            }
        }

        this.clearAuthData();
    }

    static async getProfile(): Promise<User> {
        const token = this.getToken();
        if (!token) {
            throw new Error('No authentication token');
        }

        const response = await fetch(`${API_BASE_URL}/api/auth/profile/`, {
            headers: {
                'Authorization': `Token ${token}`,
            },
        });

        if (!response.ok) {
            if (response.status === 401) {
                this.clearAuthData();
                throw new Error('Authentication expired');
            }
            throw new Error('Failed to fetch profile');
        }

        return await response.json();
    }

    static async updateProfile(data: Partial<User>): Promise<User> {
        const token = this.getToken();
        if (!token) {
            throw new Error('No authentication token');
        }

        const response = await fetch(`${API_BASE_URL}/api/auth/profile/`, {
            method: 'PUT',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Profile update failed');
        }

        const updatedUser = await response.json();
        this.storeUser(updatedUser);
        return updatedUser;
    }

    // New method for profile picture upload
    static async uploadProfilePicture(file: File): Promise<User> {
        const token = this.getToken();
        if (!token) {
            throw new Error('No authentication token');
        }

        // Convert file to base64
        const base64 = await this.fileToBase64(file);

        const response = await fetch(`${API_BASE_URL}/api/auth/profile/picture/upload/`, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                profile_picture: base64
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Profile picture upload failed');
        }

        // Get updated user profile
        const updatedUser = await this.getProfile();
        this.storeUser(updatedUser);
        return updatedUser;
    }

    // New method to delete profile picture
    static async deleteProfilePicture(): Promise<User> {
        const token = this.getToken();
        if (!token) {
            throw new Error('No authentication token');
        }

        const response = await fetch(`${API_BASE_URL}/api/auth/profile/picture/delete/`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Token ${token}`,
            },
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to delete profile picture');
        }

        // Get updated user profile
        const updatedUser = await this.getProfile();
        this.storeUser(updatedUser);
        return updatedUser;
    }

    // Helper method to convert file to base64
    private static fileToBase64(file: File): Promise<string> {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result as string);
            reader.onerror = error => reject(error);
        });
    }

    static getToken(): string | null {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem(this.TOKEN_KEY);
    }

    static getCurrentUser(): User | null {
        if (typeof window === 'undefined') return null;
        const userData = localStorage.getItem(this.USER_KEY);
        return userData ? JSON.parse(userData) : null;
    }

    static isAuthenticated(): boolean {
        return !!this.getToken();
    }

    private static storeAuthData(token: string, user: User): void {
        if (typeof window === 'undefined') return;
        localStorage.setItem(this.TOKEN_KEY, token);
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    }

    private static storeUser(user: User): void {
        if (typeof window === 'undefined') return;
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    }

    private static clearAuthData(): void {
        if (typeof window === 'undefined') return;
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
    }
}