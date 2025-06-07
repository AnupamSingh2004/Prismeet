'use client';

import { useAuth } from '@/hooks/useAuth';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

export default function Home() {
    const { user, loading, logout } = useAuth();
    const router = useRouter();
    const [imageError, setImageError] = useState(false);

    useEffect(() => {
        // Optional: redirect somewhere if logged in
    }, [user, loading, router]);

    useEffect(() => {
        if (user) {
            console.log('User profile picture URL:', user.profile_picture);
            console.log('Full user object:', user);
        }
    }, [user]);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
            </div>
        );
    }

    const formatFieldName = (key: string) => {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    };

    const formatFieldValue = (key: string | string[], value: string | number | boolean | Date | null | undefined) => {
        if (value === null || value === undefined) return 'Not set';
        if (typeof value === 'boolean') return value ? 'Yes' : 'No';
        if (key.includes('at') && typeof value === 'string') {
            try {
                return new Date(value).toLocaleString();
            } catch {
                return value;
            }
        }
        return String(value);
    };

    const shouldDisplayField = (key: string, value: string | boolean | null | undefined) => {
        const hiddenFields = ['password', 'token', 'id'];
        return !hiddenFields.some(field => key.toLowerCase().includes(field)) &&
            value !== null &&
            value !== undefined &&
            value !== '';
    };

    const handleImageError = () => {
        setImageError(true);
    };

    const ProfilePicture = () => {
        const hasProfilePicture = user?.profile_picture && !imageError;
        const initials = `${user?.first_name?.[0] || 'U'}${user?.last_name?.[0] || 'U'}`;

        if (hasProfilePicture) {
            return (
                <div className="relative w-24 h-24 rounded-full overflow-hidden border-4 border-gray-200">
                    <Image
                        src={user.profile_picture!}
                        alt={`${user.first_name} ${user.last_name}`}
                        fill
                        className="object-cover"
                        onError={handleImageError}
                        unoptimized={true} // Add this for external URLs
                    />
                </div>
            );
        }

        return (
            <div className="w-24 h-24 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xl font-semibold border-4 border-gray-200">
                {initials}
            </div>
        );
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-md">
                <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                    Welcome to Prismeet
                </h2>
                <p className="mt-2 text-center text-sm text-gray-600">
                    AI-powered meeting platform
                </p>
            </div>

            <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-2xl">
                <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 space-y-6">
                    {user ? (
                        <>
                            <div className="text-center">
                                <div className="flex justify-center mb-4">
                                    <ProfilePicture />
                                </div>

                                <h3 className="text-2xl font-bold text-gray-900">
                                    {user.full_name || `${user.first_name} ${user.last_name}`}
                                </h3>
                                <p className="text-gray-600">{user.email}</p>
                                {user.provider && (
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-2 ${
                                        user.provider === 'google'
                                            ? 'bg-red-100 text-red-800'
                                            : 'bg-blue-100 text-blue-800'
                                    }`}>
                                        {user.provider === 'google' ? '🔗 Google Account' : '📧 Email Account'}
                                    </span>
                                )}
                            </div>

                            {/* User Details */}
                            <div>
                                <h4 className="text-lg font-semibold text-gray-800 mb-4 border-b pb-2">
                                    Account Details
                                </h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {Object.entries(user)
                                        .filter(([key, value]) => shouldDisplayField(key, value))
                                        .map(([key, value]) => (
                                            <div key={key} className="bg-gray-50 p-3 rounded-lg">
                                                <dt className="text-sm font-medium text-gray-500 mb-1">
                                                    {formatFieldName(key)}
                                                </dt>
                                                <dd className="text-sm text-gray-900 break-words">
                                                    {key === 'profile_picture' ? (
                                                        <a
                                                            href={value}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="text-indigo-600 hover:text-indigo-500 underline"
                                                        >
                                                            View Image
                                                        </a>
                                                    ) : (
                                                        formatFieldValue(key, value)
                                                    )}
                                                </dd>
                                            </div>
                                        ))}
                                </div>
                            </div>

                            {/* Profile Object (if exists) */}
                            {user.profile && Object.keys(user.profile).length > 0 && (
                                <div>
                                    <h4 className="text-lg font-semibold text-gray-800 mb-4 border-b pb-2">
                                        Profile Information
                                    </h4>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {Object.entries(user.profile)
                                            .filter(([key, value]) => shouldDisplayField(key, value))
                                            .map(([key, value]) => (
                                                <div key={key} className="bg-gray-50 p-3 rounded-lg">
                                                    <dt className="text-sm font-medium text-gray-500 mb-1">
                                                        {formatFieldName(key)}
                                                    </dt>
                                                    <dd className="text-sm text-gray-900">
                                                        {formatFieldValue(key, value)}
                                                    </dd>
                                                </div>
                                            ))}
                                    </div>
                                </div>
                            )}

                            {/* Debug Info (remove in production) */}
                            {process.env.NODE_ENV === 'development' && (
                                <div className="bg-yellow-50 p-4 rounded-lg">
                                    <h5 className="font-semibold text-yellow-800">Debug Info:</h5>
                                    <p className="text-sm text-yellow-700">
                                        Profile Picture URL: {user.profile_picture || 'Not set'}
                                    </p>
                                    <p className="text-sm text-yellow-700">
                                        Provider: {user.provider}
                                    </p>
                                    <p className="text-sm text-yellow-700">
                                        Image Error: {imageError ? 'Yes' : 'No'}
                                    </p>
                                </div>
                            )}

                            {/* Action Buttons */}
                            <div className="flex space-x-4 pt-6 border-t">
                                <button
                                    onClick={() => router.push('/profile')}
                                    className="flex-1 flex justify-center py-2 px-4 border border-indigo-600 rounded-md shadow-sm text-sm font-medium text-indigo-600 bg-white hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                >
                                    Edit Profile
                                </button>
                                <button
                                    onClick={logout}
                                    className="flex-1 flex justify-center py-2 px-4 border border-red-600 rounded-md shadow-sm text-sm font-medium text-red-600 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                                >
                                    Logout
                                </button>
                            </div>
                        </>
                    ) : (
                        <>
                            <div className="text-center">
                                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                                    Get Started with Prismeet
                                </h3>
                                <p className="text-gray-600 mb-6">
                                    Sign in to access your personalized meeting dashboard
                                </p>
                            </div>

                            <div className="space-y-4">
                                <a
                                    href="/login"
                                    className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                                >
                                    Sign In
                                </a>
                                <a
                                    href="/register"
                                    className="w-full flex justify-center py-3 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                                >
                                    Create Account
                                </a>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}