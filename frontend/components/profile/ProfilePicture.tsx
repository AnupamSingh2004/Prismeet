'use client';
import React, { useState } from 'react';
import Image from 'next/image';
import { Camera } from 'lucide-react';
import { User } from '@/types/user';

interface ProfilePictureProps {
    user: User;
    onUpload?: () => void;
    size?: 'sm' | 'md' | 'lg';
    showUploadButton?: boolean;
}

export const ProfilePicture: React.FC<ProfilePictureProps> = ({
                                                                  user,
                                                                  onUpload,
                                                                  size = 'md',
                                                                  showUploadButton = true
                                                              }) => {
    const [imageError, setImageError] = useState(false);

    const handleImageError = () => {
        setImageError(true);
    };

    const handleUploadClick = () => {
        if (onUpload) {
            onUpload();
        } else {
            // Default upload handler
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.onchange = (e) => {
                const file = (e.target as HTMLInputElement).files?.[0];
                if (file) {
                    console.log('Profile picture selected:', file);
                    // Handle file upload logic here
                }
            };
            input.click();
        }
    };

    // Use the same logic as your working home page
    const hasProfilePicture = user?.profile_picture && !imageError;
    const initials = `${user?.first_name?.[0] || ''}${user?.last_name?.[0] || ''}`;

    // Size configurations
    const sizeConfig = {
        sm: {
            container: 'w-16 h-16',
            text: 'text-lg',
            button: 'w-6 h-6 -bottom-1 -right-1',
            icon: 'w-3 h-3'
        },
        md: {
            container: 'w-24 h-24',
            text: 'text-2xl',
            button: 'w-10 h-10 -bottom-2 -right-2',
            icon: 'w-5 h-5'
        },
        lg: {
            container: 'w-32 h-32',
            text: 'text-3xl',
            button: 'w-12 h-12 -bottom-2 -right-2',
            icon: 'w-6 h-6'
        }
    };

    const config = sizeConfig[size];

    // Debug logging (remove in production)
    if (process.env.NODE_ENV === 'development') {
        console.log('ProfilePicture Debug:', {
            hasProfilePicture,
            profilePictureUrl: user?.profile_picture,
            imageError,
            initials
        });
    }

    return (
        <div className="relative group">
            {hasProfilePicture ? (
                <div className={`${config.container} relative rounded-2xl overflow-hidden shadow-2xl`}>
                    <Image
                        src={user.profile_picture!}
                        alt={`${user.first_name} ${user.last_name}`}
                        fill
                        className="object-cover transition-transform group-hover:scale-105"
                        onError={handleImageError}
                        unoptimized={true} // Important for external URLs
                    />
                </div>
            ) : (
                <div className={`${config.container} bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center shadow-2xl rounded-2xl ${config.text} font-bold text-white`}>
                    {initials}
                </div>
            )}

            {showUploadButton && (
                <button
                    onClick={handleUploadClick}
                    className={`absolute ${config.button} bg-purple-600 hover:bg-purple-700 rounded-xl flex items-center justify-center text-white transition-all duration-200 shadow-lg hover:shadow-purple-500/25 group-hover:scale-110`}
                >
                    <Camera className={config.icon} />
                </button>
            )}
        </div>
    );
};