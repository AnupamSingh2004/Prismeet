'use client';

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { User } from '@/types/auth';
import { AuthService } from '@/lib/auth';

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<void>;
    register: (data: any) => Promise<void>;
    logout: () => Promise<void>;
    updateUser: (data: Partial<User>) => Promise<void>;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const initAuth = async () => {
            try {
                if (AuthService.isAuthenticated()) {
                    const currentUser = AuthService.getCurrentUser();
                    if (currentUser) {
                        // Verify token is still valid by fetching fresh profile
                        const freshUser = await AuthService.getProfile();
                        setUser(freshUser);
                    }
                }
            } catch (error) {
                console.error('Auth initialization error:', error);
                await AuthService.logout();
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

    const register = async (data: any) => {
        await AuthService.register(data);
    };

    const logout = async () => {
        await AuthService.logout();
        setUser(null);
    };

    const updateUser = async (data: Partial<User>) => {
        const updatedUser = await AuthService.updateProfile(data);
        setUser(updatedUser);
    };

    return (
        <AuthContext.Provider
            value={{
        user,
            loading,
            login,
            register,
            logout,
            updateUser,
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