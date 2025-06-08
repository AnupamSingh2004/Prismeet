'use client';
import React from 'react';
import { NotificationToggle } from '@/components/profile/NotificationToggle';
import { UserFormData } from '@/types/user';

interface NotificationPreferencesProps {
    formData: UserFormData;
    savingFields: Set<string>;
    savedFields: Set<string>;
    onNotificationToggle: (field: string) => Promise<void>;
}

export const NotificationPreferences: React.FC<NotificationPreferencesProps> = ({
                                                                                    formData,
                                                                                    savingFields,
                                                                                    savedFields,
                                                                                    onNotificationToggle
                                                                                }) => {
    return (
        <div className="space-y-6">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700/30 p-8 shadow-xl">
                <h2 className="text-xl font-semibold text-white mb-8">Notification Preferences</h2>
                <div className="space-y-8">
                    <NotificationToggle
                        field="profile.email_notifications"
                        checked={formData.profile.email_notifications}
                        label="Email Notifications"
                        description="Receive email updates about your meetings and account"
                        isSaving={savingFields.has('profile.email_notifications')}
                        isSaved={savedFields.has('profile.email_notifications')}
                        onToggle={onNotificationToggle}
                    />
                    <NotificationToggle
                        field="profile.meeting_reminders"
                        checked={formData.profile.meeting_reminders}
                        label="Meeting Reminders"
                        description="Get notified before your scheduled meetings"
                        isSaving={savingFields.has('profile.meeting_reminders')}
                        isSaved={savedFields.has('profile.meeting_reminders')}
                        onToggle={onNotificationToggle}
                    />
                    <NotificationToggle
                        field="profile.recording_notifications"
                        checked={formData.profile.recording_notifications}
                        label="Recording Notifications"
                        description="Get notified when meeting recordings are ready"
                        isSaving={savingFields.has('profile.recording_notifications')}
                        isSaved={savedFields.has('profile.recording_notifications')}
                        onToggle={onNotificationToggle}
                    />
                </div>
            </div>
        </div>
    );
};