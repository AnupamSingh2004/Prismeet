'use client';
import React from 'react';
import { ProfileHeader } from './ProfileHeader';
import { ProfileBasicInfo } from './ProfileBasicInfo';
import { User, UserFormData } from '@/types/user';

interface ProfileTabContentProps {
    user: User;
    formData: UserFormData;
    editingFields: Set<string>;
    savingFields: Set<string>;
    savedFields: Set<string>;
    onEdit: (field: string) => void;
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
    onSave: (field: string) => Promise<void>;
    onCancel: (field: string) => void;
    onProfilePictureUpload: () => void;
}

export const ProfileTabContent: React.FC<ProfileTabContentProps> = ({
                                                                        user,
                                                                        formData,
                                                                        editingFields,
                                                                        savingFields,
                                                                        savedFields,
                                                                        onEdit,
                                                                        onChange,
                                                                        onSave,
                                                                        onCancel,
                                                                        onProfilePictureUpload
                                                                    }) => {
    return (
        <div className="space-y-6">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700/30 p-8 shadow-xl">
                <h2 className="text-xl font-semibold text-white mb-8">Profile Information</h2>

                <ProfileHeader
                    user={user}
                    formData={formData}
                    onProfilePictureUpload={onProfilePictureUpload}
                />

                <ProfileBasicInfo
                    user={user}
                    formData={formData}
                    editingFields={editingFields}
                    savingFields={savingFields}
                    savedFields={savedFields}
                    onEdit={onEdit}
                    onChange={onChange}
                    onSave={onSave}
                    onCancel={onCancel}
                />
            </div>
        </div>
    );
};