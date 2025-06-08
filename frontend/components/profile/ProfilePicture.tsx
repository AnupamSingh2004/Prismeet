'use client';
import React, { useState } from 'react';
import Image from 'next/image';
import { Camera, Trash2, Loader2 } from 'lucide-react';
import { User } from '@/types/user';
import {AuthService} from "@/lib/auth";


interface ProfilePictureProps {
    user: User;
    onUpload?: (updatedUser: User) => void;
    size?: 'sm' | 'md' | 'lg';
    showUploadButton?: boolean;
    showDeleteButton?: boolean;
}

export const ProfilePicture: React.FC<ProfilePictureProps> = ({
                                                                  user,
                                                                  onUpload,
                                                                  size = 'md',
                                                                  showUploadButton = true,
                                                                  showDeleteButton = false
                                                              }) => {
    const [imageError, setImageError] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [deleting, setDeleting] = useState(false);

    const handleImageError = () => {
        setImageError(true);
    };

    const handleFileSelect = async (file: File) => {
        if (!file) return;

        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            alert('Please select a valid image file (JPEG, PNG, GIF, or WebP)');
            return;
        }

        // Validate file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
            alert('Image size must be less than 5MB');
            return;
        }

        setUploading(true);
        try {
            const updatedUser = await AuthService.uploadProfilePicture(file);
            setImageError(false); // Reset error state
            if (onUpload) {
                onUpload(updatedUser);
            }
        } catch (error) {
            console.error('Profile picture upload failed:', error);
            alert(error instanceof Error ? error.message : 'Failed to upload profile picture');
        } finally {
            setUploading(false);
        }
    };

    const handleUploadClick = () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/jpeg,image/jpg,image/png,image/gif,image/webp';
        input.onchange = (e) => {
            const file = (e.target as HTMLInputElement).files?.[0];
            if (file) {
                handleFileSelect(file);
            }
        };
        input.click();
    };

    const handleDeleteClick = async () => {
        if (!user.profile_picture) return;

        if (!confirm('Are you sure you want to delete your profile picture?')) {
            return;
        }

        setDeleting(true);
        try {
            const updatedUser = await AuthService.deleteProfilePicture();
            if (onUpload) {
                onUpload(updatedUser);
            }
        } catch (error) {
            console.error('Profile picture deletion failed:', error);
            alert(error instanceof Error ? error.message : 'Failed to delete profile picture');
        } finally {
            setDeleting(false);
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
            button: 'w-6 h-6',
            buttonPosition: '-bottom-1 -right-1',
            icon: 'w-3 h-3'
        },
        md: {
            container: 'w-24 h-24',
            text: 'text-2xl',
            button: 'w-10 h-10',
            buttonPosition: '-bottom-2 -right-2',
            icon: 'w-5 h-5'
        },
        lg: {
            container: 'w-32 h-32',
            text: 'text-3xl',
            button: 'w-12 h-12',
            buttonPosition: '-bottom-2 -right-2',
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
            initials,
            uploading,
            deleting
        });
    }

    return (
        <div className="relative group">
            {/* Loading overlay */}
            {(uploading || deleting) && (
                <div className={`absolute inset-0 ${config.container} bg-black/50 flex items-center justify-center rounded-2xl z-10`}>
                    <div className="flex flex-col items-center space-y-2">
                        <Loader2 className={`${config.icon} animate-spin text-white`} />
                        <span className="text-xs text-white">
                            {uploading ? 'Uploading...' : 'Deleting...'}
                        </span>
                    </div>
                </div>
            )}

            {hasProfilePicture ? (
                <div className={`${config.container} relative rounded-2xl overflow-hidden shadow-2xl`}>
                    <Image
                        src={user.profile_picture!}
                        alt={`${user.first_name} ${user.last_name}`}
                        fill
                        className="object-cover transition-transform group-hover:scale-105"
                        onError={handleImageError}
                        unoptimized={true} // Important for base64 data URLs
                    />
                </div>
            ) : (
                <div className={`${config.container} bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center shadow-2xl rounded-2xl ${config.text} font-bold text-white`}>
                    {initials}
                </div>
            )}

            {/* Upload button */}
            {showUploadButton && (
                <button
                    onClick={handleUploadClick}
                    disabled={uploading || deleting}
                    className={`absolute ${config.buttonPosition} ${config.button} bg-purple-600 hover:bg-purple-700 disabled:bg-gray-500 rounded-xl flex items-center justify-center text-white transition-all duration-200 shadow-lg hover:shadow-purple-500/25 group-hover:scale-110 disabled:scale-100 disabled:cursor-not-allowed`}
                >
                    <Camera className={config.icon} />
                </button>
            )}

            {/* Delete button */}
            {showDeleteButton && hasProfilePicture && (
                <button
                    onClick={handleDeleteClick}
                    disabled={uploading || deleting}
                    className={`absolute ${config.buttonPosition} ${config.button} bg-red-600 hover:bg-red-700 disabled:bg-gray-500 rounded-xl flex items-center justify-center text-white transition-all duration-200 shadow-lg hover:shadow-red-500/25 group-hover:scale-110 disabled:scale-100 disabled:cursor-not-allowed ml-14`}
                >
                    <Trash2 className={config.icon} />
                </button>
            )}
        </div>
    );
};