'use client';
import React from 'react';
import { Globe, Clock } from 'lucide-react';
import { EditableField } from '@/components/profile/EditableField';
import { UserFormData, SelectOption } from '@/types/user';

interface MeetingPreferencesProps {
    formData: UserFormData;
    editingFields: Set<string>;
    savingFields: Set<string>;
    savedFields: Set<string>;
    onEdit: (field: string) => void;
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
    onSave: (field: string) => Promise<void>;
    onCancel: (field: string) => void;
}

export const MeetingPreferences: React.FC<MeetingPreferencesProps> = ({
                                                                          formData,
                                                                          editingFields,
                                                                          savingFields,
                                                                          savedFields,
                                                                          onEdit,
                                                                          onChange,
                                                                          onSave,
                                                                          onCancel
                                                                      }) => {
    const timezoneOptions: SelectOption[] = [
        { value: '', label: 'Select Timezone' },
        { value: 'UTC', label: 'UTC' },
        { value: 'America/New_York', label: 'Eastern Time' },
        { value: 'America/Chicago', label: 'Central Time' },
        { value: 'America/Denver', label: 'Mountain Time' },
        { value: 'America/Los_Angeles', label: 'Pacific Time' },
        { value: 'Asia/Kolkata', label: 'India Standard Time' },
        { value: 'Europe/London', label: 'London Time' }
    ];

    const durationOptions: SelectOption[] = [
        { value: 15, label: '15 minutes' },
        { value: 30, label: '30 minutes' },
        { value: 45, label: '45 minutes' },
        { value: 60, label: '1 hour' },
        { value: 90, label: '1.5 hours' },
        { value: 120, label: '2 hours' }
    ];

    return (
        <div className="space-y-6">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700/30 p-8 shadow-xl">
                <h2 className="text-xl font-semibold text-white mb-8">Meeting Preferences</h2>
                <div className="space-y-8">
                    <EditableField
                        field="timezone"
                        value={formData.timezone}
                        placeholder="Select timezone"
                        options={timezoneOptions}
                        icon={Globe}
                        isEditing={editingFields.has('timezone')}
                        isSaving={savingFields.has('timezone')}
                        isSaved={savedFields.has('timezone')}
                        onEdit={onEdit}
                        onChange={onChange}
                        onSave={onSave}
                        onCancel={onCancel}
                    />
                    <EditableField
                        field="default_meeting_duration"
                        value={formData.default_meeting_duration}
                        options={durationOptions}
                        icon={Clock}
                        isEditing={editingFields.has('default_meeting_duration')}
                        isSaving={savingFields.has('default_meeting_duration')}
                        isSaved={savedFields.has('default_meeting_duration')}
                        onEdit={onEdit}
                        onChange={onChange}
                        onSave={onSave}
                        onCancel={onCancel}
                    />
                </div>
            </div>
        </div>
    );
};