'use client';

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { User, RegisterRequest } from '@/types/auth';
import { AuthService } from '@/lib/auth';
import { GoogleAuth } from '@/lib/googleAuth';

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<void>;
    register: (data: RegisterRequest) => Promise<void>;
    googleLogin: (token: string) => Promise<void>;
    logout: () => Promise<void>;
    updateUser: (data: Partial<User>) => Promise<void>;
    refreshUser: () => Promise<void>; // Added this missing method
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const initAuth = async () => {
            try {
                // Initialize Google Auth for token generation
                const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
                if (clientId) {
                    await GoogleAuth.initialize(clientId);
                }

                // Check existing authentication
                if (AuthService.isAuthenticated()) {
                    const currentUser = AuthService.getCurrentUser();
                    if (currentUser) {
                        try {
                            const freshUser = await AuthService.getProfile();
                            setUser(freshUser);
                        } catch{
                            await AuthService.logout();
                        }
                    }
                }
            } catch (error) {
                console.error('Auth initialization error:', error);
            } finally {
                setLoading(false);
            }
        };

        initAuth();
    }, []);

    const login = async (email: string, password: string) => {
        const response = await AuthService.login({ email, password });
        setUser(response.user);
    };

    const register = async (data: RegisterRequest) => {
        const response = await AuthService.register(data);
        setUser(response.user);
    };

    const googleLogin = async (googleToken: string) => {
        try {
            const response = await AuthService.googleAuth(googleToken);
            setUser(response.user);
        } catch (error) {
            console.error('Google login error:', error);
            throw error;
        }
    };

    const logout = async () => {
        await AuthService.logout();
        setUser(null);
    };

    const updateUser = async (data: Partial<User>) => {
        const updatedUser = await AuthService.updateProfile(data);
        setUser(updatedUser);
    };

    // Added the missing refreshUser method
    const refreshUser = async () => {
        try {
            if (AuthService.isAuthenticated()) {
                const freshUser = await AuthService.getProfile();
                setUser(freshUser);
            }
        } catch (error) {
            console.error('Failed to refresh user:', error);
            // If refresh fails, user might be logged out
            await AuthService.logout();
            setUser(null);
        }
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                login,
                register,
                googleLogin,
                logout,
                updateUser,
                refreshUser, // Added to the provider value
                isAuthenticated: !!user,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}