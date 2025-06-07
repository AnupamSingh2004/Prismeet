'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import AuthGuard from '@/components/auth/AuthGuard';

interface ApiErrorResponse {
    error?: string;
    detail?: string;
    [key: string]: unknown;
}

export default function VerifyEmailPage() {
    const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'invalid'>('loading');
    const [message, setMessage] = useState('');
    const [resending, setResending] = useState(false);

    const router = useRouter();
    const searchParams = useSearchParams();
    const token = searchParams.get('token');

    const verifyEmail = useCallback(async (verificationToken: string) => {
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/verify-email/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token: verificationToken }),
            });

            const data = await response.json() as ApiErrorResponse;

            if (response.ok) {
                setStatus('success');
                setMessage('Your email has been verified successfully!');

                // Redirect to login after 3 seconds
                setTimeout(() => {
                    router.push('/login');
                }, 3000);
            } else {
                setStatus('error');
                setMessage(data.error || 'Verification failed');
            }
        } catch (err) {
            console.error('Email verification error:', err);
            setStatus('error');
            setMessage('An error occurred during verification');
        }
    }, [router]);

    useEffect(() => {
        if (!token) {
            setStatus('invalid');
            setMessage('Invalid verification link');
            return;
        }

        verifyEmail(token);
    }, [token, verifyEmail]);

    const resendVerification = async () => {
        setResending(true);
        try {
            // Check if we're in browser environment before accessing localStorage
            const authToken = typeof window !== 'undefined' ? localStorage.getItem('authToken') : null;

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/resend-verification/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(authToken && { 'Authorization': `Token ${authToken}` }),
                },
            });

            const data = await response.json() as ApiErrorResponse;

            if (response.ok) {
                setMessage('Verification email sent successfully! Please check your inbox.');
            } else {
                setMessage(data.error || 'Failed to resend verification email');
            }
        } catch (err) {
            console.error('Resend verification error:', err);
            setMessage('Failed to resend verification email');
        } finally {
            setResending(false);
        }
    };

    const getStatusIcon = () => {
        switch (status) {
            case 'loading':
                return (
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                );
            case 'success':
                return (
                    <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
                        <svg className="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                    </div>
                );
            case 'error':
                return (
                    <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
                        <svg className="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </div>
                );
            case 'invalid':
                return (
                    <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-yellow-100 mb-4">
                        <svg className="h-8 w-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                        </svg>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <AuthGuard requireAuth={false}>
            <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
                <div className="sm:mx-auto sm:w-full sm:max-w-md">
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Email Verification
                    </h2>
                </div>

                <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
                    <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
                        <div className="text-center">
                            {getStatusIcon()}

                            <p className="text-gray-600 mb-6">
                                {message}
                            </p>

                            {status === 'success' && (
                                <p className="text-sm text-gray-500 mb-4">
                                    You will be redirected to the login page in a few seconds...
                                </p>
                            )}

                            {status === 'error' && (
                                <div className="space-y-4">
                                    <button
                                        onClick={resendVerification}
                                        disabled={resending}
                                        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                                    >
                                        {resending ? 'Sending...' : 'Resend Verification Email'}
                                    </button>
                                </div>
                            )}

                            <div className="mt-6 space-y-2">
                                <Link
                                    href="/login"
                                    className="text-indigo-600 hover:text-indigo-500 text-sm block"
                                >
                                    Back to Login
                                </Link>
                                <Link
                                    href="/register"
                                    className="text-indigo-600 hover:text-indigo-500 text-sm block"
                                >
                                    Create New Account
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </AuthGuard>
    );
}