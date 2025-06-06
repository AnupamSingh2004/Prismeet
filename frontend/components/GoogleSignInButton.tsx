'use client';

import { useEffect, useRef, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { GoogleAuth } from '@/lib/googleAuth';

interface GoogleSignInButtonProps {
    onSuccess?: () => void;
    onError?: (error: Error) => void;
    disabled?: boolean;
    className?: string;
}

export function GoogleSignInButton({
                                       onSuccess,
                                       onError,
                                       disabled,
                                       className
                                   }: GoogleSignInButtonProps) {
    const [loading, setLoading] = useState(false);
    const buttonRef = useRef<HTMLDivElement>(null);
    const { googleLogin } = useAuth();

    useEffect(() => {
        if (!buttonRef.current || disabled) return;

        const handleGoogleResponse = async (token: string) => {
            setLoading(true);
            try {
                await googleLogin(token);
                onSuccess?.();
            } catch (error) {
                console.error('Google sign-in error:', error);
                onError?.(error as Error);
            } finally {
                setLoading(false);
            }
        };

        try {
            GoogleAuth.renderButton(buttonRef.current, handleGoogleResponse);
        } catch (error) {
            console.error('Failed to render Google button:', error);
            onError?.(error as Error);
        }
    }, [disabled, googleLogin, onSuccess, onError]);

    return (
        <div className={`google-signin-container ${className}`}>
            <div
                ref={buttonRef}
                className={`w-full ${loading ? 'opacity-50 pointer-events-none' : ''}`}
            />
            {loading && (
                <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75">
                    <div className="text-sm text-gray-600">Signing in...</div>
                </div>
            )}
        </div>
    );
}
