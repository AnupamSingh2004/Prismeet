'use client';
import React from 'react';
import { ProfilePicture } from './ProfilePicture';
import { User, UserFormData } from '@/types/user';

interface ProfileHeaderProps {
    user: User;
    formData: UserFormData;
    onProfilePictureUpdate: (updatedUser: User) => void;
}

export const ProfileHeader: React.FC<ProfileHeaderProps> = ({
                                                                user,
                                                                formData,
                                                                onProfilePictureUpdate
                                                            }) => {
    const getDisplayName = () => {
        return user.full_name || `${user.first_name} ${user.last_name}`;
    };

    const getJobInfo = () => {
        const { job_title, company } = formData.profile;

        if (job_title && company) {
            return `${job_title} at ${company}`;
        }
        return job_title || company || 'Update your professional info';
    };

    const handleProfilePictureUpload = () => {
        // This will be handled by the ProfilePicture component
        // We're keeping this for backward compatibility
    };

    return (
        <div className="flex items-center space-x-6 mb-10">
            <ProfilePicture
                user={user}
                onUpload={onProfilePictureUpdate}
                size="lg"
                showUploadButton={true}
                showDeleteButton={true}
            />
            <div>
                <h3 className="text-2xl font-bold text-white mb-1">
                    {getDisplayName()}
                </h3>
                <p className="text-gray-400 text-lg mb-2">
                    {getJobInfo()}
                </p>
                <div className="flex space-x-4">
                    <button
                        onClick={handleProfilePictureUpload}
                        className="text-sm text-purple-400 hover:text-purple-300 font-medium transition-colors duration-200"
                    >
                        Change photo
                    </button>
                    {user.profile_picture && (
                        <span className="text-sm text-gray-500">
                            or delete current photo
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
};