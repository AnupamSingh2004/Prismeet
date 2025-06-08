'use client';
import React from 'react';
import { User, Phone, Briefcase, Building } from 'lucide-react';
import { EditableField } from '@/components/profile/EditableField';
import { EmailField } from './EmailField';
import { User as UserType, UserFormData } from '@/types/user';

interface ProfileBasicInfoProps {
    user: UserType;
    formData: UserFormData;
    editingFields: Set<string>;
    savingFields: Set<string>;
    savedFields: Set<string>;
    onEdit: (field: string) => void;
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
    onSave: (field: string) => Promise<void>;
    onCancel: (field: string) => void;
}

export const ProfileBasicInfo: React.FC<ProfileBasicInfoProps> = ({
                                                                      user,
                                                                      formData,
                                                                      editingFields,
                                                                      savingFields,
                                                                      savedFields,
                                                                      onEdit,
                                                                      onChange,
                                                                      onSave,
                                                                      onCancel
                                                                  }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Left Column */}
            <div className="space-y-6">
                <EditableField
                    field="first_name"
                    value={formData.first_name}
                    placeholder="First name"
                    icon={User}
                    isEditing={editingFields.has('first_name')}
                    isSaving={savingFields.has('first_name')}
                    isSaved={savedFields.has('first_name')}
                    onEdit={onEdit}
                    onChange={onChange}
                    onSave={onSave}
                    onCancel={onCancel}
                />
                <EditableField
                    field="last_name"
                    value={formData.last_name}
                    placeholder="Last name"
                    icon={User}
                    isEditing={editingFields.has('last_name')}
                    isSaving={savingFields.has('last_name')}
                    isSaved={savedFields.has('last_name')}
                    onEdit={onEdit}
                    onChange={onChange}
                    onSave={onSave}
                    onCancel={onCancel}
                />
                <EditableField
                    field="phone_number"
                    value={formData.phone_number}
                    placeholder="+91 12345 67890"
                    type="tel"
                    icon={Phone}
                    isEditing={editingFields.has('phone_number')}
                    isSaving={savingFields.has('phone_number')}
                    isSaved={savedFields.has('phone_number')}
                    onEdit={onEdit}
                    onChange={onChange}
                    onSave={onSave}
                    onCancel={onCancel}
                />
            </div>

            {/* Right Column */}
            <div className="space-y-6">
                <EmailField user={user} />
                <EditableField
                    field="profile.job_title"
                    value={formData.profile.job_title || ''}
                    placeholder="Job title"
                    icon={Briefcase}
                    isEditing={editingFields.has('profile.job_title')}
                    isSaving={savingFields.has('profile.job_title')}
                    isSaved={savedFields.has('profile.job_title')}
                    onEdit={onEdit}
                    onChange={onChange}
                    onSave={onSave}
                    onCancel={onCancel}
                />
                <EditableField
                    field="profile.company"
                    value={formData.profile.company || ''}
                    placeholder="Company"
                    icon={Building}
                    isEditing={editingFields.has('profile.company')}
                    isSaving={savingFields.has('profile.company')}
                    isSaved={savedFields.has('profile.company')}
                    onEdit={onEdit}
                    onChange={onChange}
                    onSave={onSave}
                    onCancel={onCancel}
                />
            </div>
        </div>
    );
};