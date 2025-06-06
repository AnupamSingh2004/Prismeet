'use client';

import { useAuth } from '@/hooks/useAuth';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Optional: redirect somewhere if logged in
  }, [user, loading, router]);

  if (loading) {
    return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
        </div>
    );
  }

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

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 space-y-4">
            {user ? (
                <>
                  <div className="text-lg font-semibold text-gray-800 text-center">User Details</div>
                  <div className="text-sm text-gray-700 space-y-2">
                    {Object.entries(user).map(([key, value]) => (
                        <div key={key} className="flex justify-between border-b pb-1">
                          <span className="font-medium capitalize">{key.replace(/_/g, ' ')}:</span>
                          <span>{String(value)}</span>
                        </div>
                    ))}
                  </div>
                  <button
                      onClick={logout}
                      className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    Logout
                  </button>
                </>
            ) : (
                <>
                  <a
                      href="/login"
                      className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Sign In
                  </a>
                  <a
                      href="/register"
                      className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Sign Up
                  </a>
                </>
            )}
          </div>
        </div>
      </div>
  );
}
