'use client';
import { useAuth } from '@/hooks/useAuth';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import AuthGuard from '@/components/auth/AuthGuard';
import { Loader2 } from 'lucide-react';
import { UserFormData, UserProfile, User } from '@/types/user';

import { ProfileNavigation } from '@/components/profile/ProfileNavigation';
import { ProfileHeader } from '@/components/profile/ProfileHeader';
import { ProfileBasicInfo } from '@/components/profile/ProfileBasicInfo';
import { MeetingPreferences } from '@/components/profile/MeetingPreferences';
import { NotificationPreferences } from '@/components/profile/NotificationPreferences';
import { SecuritySettings } from '@/components/profile/SecuritySettings';

export default function ModernProfile() {
    const { user, loading, updateUser, refreshUser } = useAuth();
    const router = useRouter();

    const [editingFields, setEditingFields] = useState<Set<string>>(new Set());
    const [isInitialized, setIsInitialized] = useState(false);
    const [activeTab, setActiveTab] = useState('profile');

    const [formData, setFormData] = useState<UserFormData>({
        first_name: '',
        last_name: '',
        phone_number: '',
        timezone: '',
        default_meeting_duration: 30,
        profile: {
            bio: '',
            company: '',
            job_title: '',
            website: '',
            email_notifications: true,
            meeting_reminders: true,
            recording_notifications: true,
        }
    });

    const [savingFields, setSavingFields] = useState<Set<string>>(new Set());
    const [savedFields, setSavedFields] = useState<Set<string>>(new Set());

    // Initialize form data when user loads
    useEffect(() => {
        if (user && !isInitialized) {
            setFormData({
                first_name: user.first_name || '',
                last_name: user.last_name || '',
                phone_number: user.phone_number || '',
                timezone: user.timezone || '',
                default_meeting_duration: user.default_meeting_duration || 30,
                profile: {
                    bio: user.profile?.bio || '',
                    company: user.profile?.company || '',
                    job_title: user.profile?.job_title || '',
                    website: user.profile?.website || '',
                    email_notifications: user.profile?.email_notifications ?? true,
                    meeting_reminders: user.profile?.meeting_reminders ?? true,
                    recording_notifications: user.profile?.recording_notifications ?? true,
                }
            });
            setIsInitialized(true);
        }
    }, [user, isInitialized]);

    const handleEdit = (field: string) => {
        setEditingFields(prev => {
            const newSet = new Set(prev);
            newSet.add(field);
            return newSet;
        });
    };

    const handleCancel = (field: string) => {
        setEditingFields(prev => {
            const newSet = new Set(prev);
            newSet.delete(field);
            if (user) {
                if (field.startsWith('profile.')) {
                    const profileField = field.replace('profile.', '') as keyof UserProfile;
                    setFormData(prev => ({
                        ...prev,
                        profile: {
                            ...prev.profile,
                            [profileField]: user.profile?.[profileField] ?? ''
                        }
                    }));
                } else {
                    switch (field) {
                        case 'first_name':
                            setFormData(prev => ({
                                ...prev,
                                first_name: user.first_name ?? ''
                            }));
                            break;
                        case 'last_name':
                            setFormData(prev => ({
                                ...prev,
                                last_name: user.last_name ?? ''
                            }));
                            break;
                        case 'phone_number':
                            setFormData(prev => ({
                                ...prev,
                                phone_number: user.phone_number ?? ''
                            }));
                            break;
                        case 'timezone':
                            setFormData(prev => ({
                                ...prev,
                                timezone: user.timezone ?? ''
                            }));
                            break;
                        case 'default_meeting_duration':
                            setFormData(prev => ({
                                ...prev,
                                default_meeting_duration: user.default_meeting_duration ?? 30
                            }));
                            break;
                        default:
                            break;
                    }
                }
            }
            return newSet;
        });
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        const isCheckbox = type === 'checkbox';
        const finalValue = isCheckbox ? (e.target as HTMLInputElement).checked : value;

        if (name.startsWith('profile.')) {
            const profileField = name.replace('profile.', '') as keyof typeof formData.profile;
            setFormData(prev => ({
                ...prev,
                profile: {
                    ...prev.profile,
                    [profileField]: type === 'number' ? parseInt(value) || 0 : finalValue
                }
            }));
        } else {
            const userField = name as keyof Omit<UserFormData, 'profile'>;
            setFormData(prev => ({
                ...prev,
                [userField]: type === 'number' ? parseInt(value) || 0 : finalValue
            }));
        }
    };

    const handleSave = async (field: string) => {
        setSavingFields(prev => new Set([...prev, field]));
        try {
            await updateUser(formData);
            setEditingFields(prev => {
                const newSet = new Set(prev);
                newSet.delete(field);
                return newSet;
            });

            setSavedFields(prev => new Set([...prev, field]));
            setTimeout(() => {
                setSavedFields(prev => {
                    const newSet = new Set(prev);
                    newSet.delete(field);
                    return newSet;
                });
            }, 2000);
        } catch (error) {
            console.error('Profile update error:', error);
            alert('Failed to update profile. Please try again.');
        } finally {
            setSavingFields(prev => {
                const newSet = new Set(prev);
                newSet.delete(field);
                return newSet;
            });
        }
    };

    const handleNotificationToggle = async (field: string) => {
        const profileField = field.replace('profile.', '') as keyof typeof formData.profile;
        const currentValue = formData.profile[profileField] as boolean;

        const newFormData = {
            ...formData,
            profile: {
                ...formData.profile,
                [profileField]: !currentValue
            }
        };
        setFormData(newFormData);

        setSavingFields(prev => new Set([...prev, field]));
        try {
            await updateUser(newFormData);
            setSavedFields(prev => new Set([...prev, field]));
            setTimeout(() => {
                setSavedFields(prev => {
                    const newSet = new Set(prev);
                    newSet.delete(field);
                    return newSet;
                });
            }, 2000);
        } catch (error) {
            console.error('Failed to update notification setting:', error);
            // Revert the change
            setFormData(formData);
        } finally {
            setSavingFields(prev => {
                const newSet = new Set(prev);
                newSet.delete(field);
                return newSet;
            });
        }
    };

    const handleChangePassword = () => {
        router.push('/reset-password');
    };

    // Updated profile picture handler
    const handleProfilePictureUpdate = async (updatedUser: User) => {
        // Update the form data with the new user data
        setFormData(prev => ({
            ...prev,
            first_name: updatedUser.first_name || '',
            last_name: updatedUser.last_name || '',
            phone_number: updatedUser.phone_number || '',
            timezone: updatedUser.timezone || '',
            default_meeting_duration: updatedUser.default_meeting_duration || 30,
            profile: {
                ...prev.profile,
                bio: updatedUser.profile?.bio || '',
                company: updatedUser.profile?.company || '',
                job_title: updatedUser.profile?.job_title || '',
                website: updatedUser.profile?.website || '',
                email_notifications: updatedUser.profile?.email_notifications ?? true,
                meeting_reminders: updatedUser.profile?.meeting_reminders ?? true,
                recording_notifications: updatedUser.profile?.recording_notifications ?? true,
            }
        }));

        // Refresh the user data from auth context
        if (refreshUser) {
            await refreshUser();
        }
    };

    const handleTabChange = (tabId: string) => {
        setActiveTab(tabId);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <div className="flex items-center space-x-3">
                    <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
                    <span className="text-gray-300 text-lg">Loading your profile...</span>
                </div>
            </div>
        );
    }

    if (!user) {
        return null;
    }

    const renderTabContent = () => {
        switch (activeTab) {
            case 'profile':
                return (
                    <div className="space-y-6">
                        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700/30 p-8 shadow-xl">
                            <h2 className="text-xl font-semibold text-white mb-8">Profile Information</h2>

                            <ProfileHeader
                                user={user}
                                formData={formData}
                                onProfilePictureUpdate={handleProfilePictureUpdate}
                            />

                            <ProfileBasicInfo
                                user={user}
                                formData={formData}
                                editingFields={editingFields}
                                savingFields={savingFields}
                                savedFields={savedFields}
                                onEdit={handleEdit}
                                onChange={handleInputChange}
                                onSave={handleSave}
                                onCancel={handleCancel}
                            />
                        </div>
                    </div>
                );

            case 'meetings':
                return (
                    <MeetingPreferences
                        formData={formData}
                        editingFields={editingFields}
                        savingFields={savingFields}
                        savedFields={savedFields}
                        onEdit={handleEdit}
                        onChange={handleInputChange}
                        onSave={handleSave}
                        onCancel={handleCancel}
                    />
                );

            case 'notifications':
                return (
                    <NotificationPreferences
                        formData={formData}
                        savingFields={savingFields}
                        savedFields={savedFields}
                        onNotificationToggle={handleNotificationToggle}
                    />
                );

            case 'security':
                return (
                    <SecuritySettings
                        onChangePassword={handleChangePassword}
                    />
                );

            default:
                return null;
        }
    };

    return (
        <AuthGuard requireAuth={true}>
            <div className="min-h-screen bg-gray-900">
                <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                        {/* Sidebar Navigation */}
                        <div className="lg:col-span-1">
                            <ProfileNavigation
                                activeTab={activeTab}
                                onTabChange={handleTabChange}
                            />
                        </div>

                        {/* Main Content */}
                        <div className="lg:col-span-3">
                            {renderTabContent()}
                        </div>
                    </div>
                </div>
            </div>
        </AuthGuard>
    );
}