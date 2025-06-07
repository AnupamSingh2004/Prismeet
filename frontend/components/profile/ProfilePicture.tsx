'use client';
import React, { useState } from 'react';
import Image from 'next/image';
import { Camera } from 'lucide-react';
import { User } from '@/types/user';

interface ProfilePictureProps {
    user: User;
}

export const ProfilePicture: React.FC<ProfilePictureProps> = ({ user }) => {
    const [imageError, setImageError] = useState(false);

    const handleImageError = () => {
        setImageError(true);
    };

    const hasProfilePicture = user?.profile_picture && !imageError;
    const initials = `${user?.first_name?.[0] || 'U'}${user?.last_name?.[0] || 'U'}`;

    return (
        <div className="relative group">
            <div className="relative w-32 h-32 rounded-2xl overflow-hidden border-4 border-white/10 shadow-2xl">
                {hasProfilePicture ? (
                    <Image
                        src={user.profile_picture!}
                        alt={`${user.first_name} ${user.last_name}`}
                        fill
                        className="object-cover transition-transform group-hover:scale-105"
                        onError={handleImageError}
                        unoptimized={true}
                    />
                ) : (
                    <div className="w-full h-full bg-gradient-to-br from-purple-500 via-pink-500 to-blue-600 text-white flex items-center justify-center text-3xl font-bold">
                        {initials}
                    </div>
                )}
            </div>
            <button className="absolute -bottom-2 -right-2 w-10 h-10 bg-purple-600 hover:bg-purple-700 rounded-full flex items-center justify-center text-white shadow-lg transition-all hover:scale-105 opacity-0 group-hover:opacity-100">
                <Camera className="w-4 h-4" />
            </button>
        </div>
    );
};