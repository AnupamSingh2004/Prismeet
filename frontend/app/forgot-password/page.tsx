'use client';

import { useState } from 'react';
import Link from 'next/link';
import AuthGuard from '@/components/auth/AuthGuard';

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/password-reset-request/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            const data = await response.json();

            if (response.ok) {
                setSubmitted(true);
            } else {
                setError(data.error || data.email?.[0] || 'Failed to send reset email');
            }
        } catch {
            setError('An error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (submitted) {
        return (
            <AuthGuard requireAuth={false}>
                <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
                    <div className="sm:mx-auto sm:w-full sm:max-w-md">
                        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                            Check Your Email
                        </h2>
                    </div>

                    <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
                        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
                            <div className="text-center">
                                <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
                                    <svg className="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                                    </svg>
                                </div>

                                <h3 className="text-lg font-medium text-gray-900 mb-2">
                                    Password Reset Email Sent
                                </h3>

                                <p className="text-gray-600 mb-6">
                                    We&apos;ve sent a password reset link to <span className="font-medium">{email}</span>.
                                    Please check your inbox and follow the instructions to reset your password.
                                </p>

                                <p className="text-sm text-gray-500 mb-6">
                                    The reset link will expire in 24 hours. If you don&apos;t see the email, check your spam folder.
                                </p>

                                <div className="space-y-2">
                                    <Link
                                        href="/login"
                                        className="text-indigo-600 hover:text-indigo-500 text-sm block"
                                    >
                                        Back to Login
                                    </Link>
                                    <button
                                        onClick={() => {
                                            setSubmitted(false);
                                            setEmail('');
                                        }}
                                        className="text-indigo-600 hover:text-indigo-500 text-sm block"
                                    >
                                        Try Different Email
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </AuthGuard>
        );
    }

    return (
        <AuthGuard requireAuth={false}>
            <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
                <div className="sm:mx-auto sm:w-full sm:max-w-md">
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Forgot Your Password?
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Enter your email address and we&apos;ll send you a link to reset your password.
                    </p>
                </div>

                <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
                    <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
                        <form className="space-y-6" onSubmit={handleSubmit}>
                            {error && (
                                <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
                                    {error}
                                </div>
                            )}

                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                                    Email address
                                </label>
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    autoComplete="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                                    placeholder="Enter your email address"
                                />
                            </div>

                            <div>
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                                >
                                    {loading ? 'Sending...' : 'Send Reset Link'}
                                </button>
                            </div>

                            <div className="text-center space-y-2">
                                <Link href="/login" className="text-indigo-600 hover:text-indigo-500 text-sm block">
                                    Back to Login
                                </Link>
                                <Link href="/register" className="text-indigo-600 hover:text-indigo-500 text-sm block">
                                    Don&apos;t have an account? Sign up
                                </Link>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </AuthGuard>
    );
}