'use client';
import { useAuth } from '@/hooks/useAuth';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import AuthGuard from '@/components/auth/AuthGuard';
import {
    Mail,
    Phone,
    Globe,
    Clock,
    User,
    Building,
    Briefcase,
    Bell,
    Loader2,
    Camera,
    Calendar,
    Shield,
    Key,
    Check
} from 'lucide-react';
import { EditableField } from '@/components/profile/EditableField';
import { NotificationToggle } from '@/components/profile/NotificationToggle';
import {UserFormData, SelectOption, UserProfile} from '@/types/user';
import Image from 'next/image';

export default function ModernProfile() {
    const { user, loading, updateUser } = useAuth();
    const router = useRouter();

    const [editingFields, setEditingFields] = useState<Set<string>>(new Set());
    const [isInitialized, setIsInitialized] = useState(false);
    const [activeTab, setActiveTab] = useState('profile');
    const [imageError, setImageError] = useState(false);

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

    // Only initialize form data once when user is first loaded
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
            // Reset field value when canceling edit
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
                    // Handle each user field explicitly with proper typing
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

            // Show success indicator
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
        router.push('/forgot-password');
    };

    const handleImageError = () => {
        setImageError(true);
    };

    const handleProfilePictureUpload = () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.onchange = (e) => {
            const file = (e.target as HTMLInputElement).files?.[0];
            if (file) {
                // Handle file upload logic here
                console.log('Profile picture selected:', file);
                // You would typically upload this to your backend
                // and then update the user's profile_picture field
            }
        };
        input.click();
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

    // Check if user has a profile picture and it hasn't failed to load
    const hasProfilePicture = user?.profile_picture && !imageError;
    const userInitials = `${user?.first_name?.[0] || ''}${user?.last_name?.[0] || ''}`;

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

    const tabs = [
        { id: 'profile', label: 'Profile', icon: User },
        { id: 'meetings', label: 'Meetings', icon: Calendar },
        { id: 'notifications', label: 'Notifications', icon: Bell },
        { id: 'security', label: 'Security', icon: Shield }
    ];

    return (
        <AuthGuard requireAuth={true}>
            <div className="min-h-screen bg-gray-900">

                <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                        {/* Sidebar Navigation */}
                        <div className="lg:col-span-1">
                            <nav className="space-y-2">
                                {tabs.map((tab) => {
                                    const Icon = tab.icon;
                                    return (
                                        <button
                                            key={tab.id}
                                            onClick={() => setActiveTab(tab.id)}
                                            className={`w-full flex items-center space-x-3 px-4 py-3 text-left rounded-xl transition-all duration-200 ${
                                                activeTab === tab.id
                                                    ? 'bg-purple-600/20 text-purple-300 border border-purple-500/30 shadow-lg shadow-purple-500/10'
                                                    : 'text-gray-400 hover:bg-gray-700/30 hover:text-gray-200'
                                            }`}
                                        >
                                            <Icon className="w-5 h-5" />
                                            <span className="font-medium">{tab.label}</span>
                                        </button>
                                    );
                                })}
                            </nav>
                        </div>

                        {/* Main Content */}
                        <div className="lg:col-span-3">
                            {activeTab === 'profile' && (
                                <div className="space-y-6">
                                    {/* Profile Header */}
                                    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700/30 p-8 shadow-xl">
                                        <h2 className="text-xl font-semibold text-white mb-8">Profile Information</h2>

                                        {/* Profile Picture */}
                                        <div className="flex items-center space-x-6 mb-10">
                                            <div className="relative group">
                                                {hasProfilePicture ? (
                                                    <div className="w-24 h-24 relative rounded-2xl overflow-hidden shadow-2xl">
                                                        <Image
                                                            src={user.profile_picture!}
                                                            alt={`${user.first_name} ${user.last_name}`}
                                                            fill
                                                            className="object-cover transition-transform group-hover:scale-105"
                                                            onError={handleImageError}
                                                            unoptimized={true}
                                                        />
                                                    </div>
                                                ) : (
                                                    <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-2xl">
                                                        <span className="text-2xl font-bold text-white">
                                                            {userInitials}
                                                        </span>
                                                    </div>
                                                )}
                                                <button
                                                    onClick={handleProfilePictureUpload}
                                                    className="absolute -bottom-2 -right-2 w-10 h-10 bg-purple-600 hover:bg-purple-700 rounded-xl flex items-center justify-center text-white transition-all duration-200 shadow-lg hover:shadow-purple-500/25 group-hover:scale-110"
                                                >
                                                    <Camera className="w-5 h-5" />
                                                </button>
                                            </div>
                                            <div>
                                                <h3 className="text-2xl font-bold text-white mb-1">
                                                    {user.full_name || `${user.first_name} ${user.last_name}`}
                                                </h3>
                                                <p className="text-gray-400 text-lg mb-2">
                                                    {formData.profile.job_title && formData.profile.company
                                                        ? `${formData.profile.job_title} at ${formData.profile.company}`
                                                        : formData.profile.job_title || formData.profile.company || 'Update your professional info'
                                                    }
                                                </p>
                                                <button
                                                    onClick={handleProfilePictureUpload}
                                                    className="text-sm text-purple-400 hover:text-purple-300 font-medium transition-colors duration-200"
                                                >
                                                    Change photo
                                                </button>
                                            </div>
                                        </div>

                                        {/* Basic Info */}
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                            <div className="space-y-6">
                                                <EditableField
                                                    field="first_name"
                                                    value={formData.first_name}
                                                    placeholder="First name"
                                                    icon={User}
                                                    isEditing={editingFields.has('first_name')}
                                                    isSaving={savingFields.has('first_name')}
                                                    isSaved={savedFields.has('first_name')}
                                                    onEdit={handleEdit}
                                                    onChange={handleInputChange}
                                                    onSave={handleSave}
                                                    onCancel={handleCancel}
                                                />
                                                <EditableField
                                                    field="last_name"
                                                    value={formData.last_name}
                                                    placeholder="Last name"
                                                    icon={User}
                                                    isEditing={editingFields.has('last_name')}
                                                    isSaving={savingFields.has('last_name')}
                                                    isSaved={savedFields.has('last_name')}
                                                    onEdit={handleEdit}
                                                    onChange={handleInputChange}
                                                    onSave={handleSave}
                                                    onCancel={handleCancel}
                                                />
                                                <EditableField
                                                    field="phone_number"
                                                    value={formData.phone_number}
                                                    placeholder="+1 (555) 123-4567"
                                                    type="tel"
                                                    icon={Phone}
                                                    isEditing={editingFields.has('phone_number')}
                                                    isSaving={savingFields.has('phone_number')}
                                                    isSaved={savedFields.has('phone_number')}
                                                    onEdit={handleEdit}
                                                    onChange={handleInputChange}
                                                    onSave={handleSave}
                                                    onCancel={handleCancel}
                                                />
                                            </div>
                                            <div className="space-y-6">
                                                <div className="space-y-3">
                                                    <label className="text-sm font-medium text-gray-300 flex items-center space-x-2">
                                                        <Mail className="w-4 h-4 text-gray-400" />
                                                        <span>Email</span>
                                                    </label>
                                                    <div className="flex items-center space-x-3 p-4 bg-gray-700/30 rounded-xl border border-gray-600/30">
                                                        <span className="text-white font-medium">{user.email}</span>
                                                        {user.is_email_verified && (
                                                            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-green-500/20 text-green-400 border border-green-500/30">
                                                                <Check className="w-3 h-3 mr-1" />
                                                                Verified
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>
                                                <EditableField
                                                    field="profile.job_title"
                                                    value={formData.profile.job_title || ''}
                                                    placeholder="Job title"
                                                    icon={Briefcase}
                                                    isEditing={editingFields.has('profile.job_title')}
                                                    isSaving={savingFields.has('profile.job_title')}
                                                    isSaved={savedFields.has('profile.job_title')}
                                                    onEdit={handleEdit}
                                                    onChange={handleInputChange}
                                                    onSave={handleSave}
                                                    onCancel={handleCancel}
                                                />
                                                <EditableField
                                                    field="profile.company"
                                                    value={formData.profile.company || ''}
                                                    placeholder="Company"
                                                    icon={Building}
                                                    isEditing={editingFields.has('profile.company')}
                                                    isSaving={savingFields.has('profile.company')}
                                                    isSaved={savedFields.has('profile.company')}
                                                    onEdit={handleEdit}
                                                    onChange={handleInputChange}
                                                    onSave={handleSave}
                                                    onCancel={handleCancel}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'meetings' && (
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
                                                onEdit={handleEdit}
                                                onChange={handleInputChange}
                                                onSave={handleSave}
                                                onCancel={handleCancel}
                                            />
                                            <EditableField
                                                field="default_meeting_duration"
                                                value={formData.default_meeting_duration}
                                                options={durationOptions}
                                                icon={Clock}
                                                isEditing={editingFields.has('default_meeting_duration')}
                                                isSaving={savingFields.has('default_meeting_duration')}
                                                isSaved={savedFields.has('default_meeting_duration')}
                                                onEdit={handleEdit}
                                                onChange={handleInputChange}
                                                onSave={handleSave}
                                                onCancel={handleCancel}
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'notifications' && (
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
                                                onToggle={handleNotificationToggle}
                                            />
                                            <NotificationToggle
                                                field="profile.meeting_reminders"
                                                checked={formData.profile.meeting_reminders}
                                                label="Meeting Reminders"
                                                description="Get notified before your scheduled meetings"
                                                isSaving={savingFields.has('profile.meeting_reminders')}
                                                isSaved={savedFields.has('profile.meeting_reminders')}
                                                onToggle={handleNotificationToggle}
                                            />
                                            <NotificationToggle
                                                field="profile.recording_notifications"
                                                checked={formData.profile.recording_notifications}
                                                label="Recording Notifications"
                                                description="Get notified when meeting recordings are ready"
                                                isSaving={savingFields.has('profile.recording_notifications')}
                                                isSaved={savedFields.has('profile.recording_notifications')}
                                                onToggle={handleNotificationToggle}
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'security' && (
                                <div className="space-y-6">
                                    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700/30 p-8 shadow-xl">
                                        <h2 className="text-xl font-semibold text-white mb-8">Security Settings</h2>
                                        <div className="space-y-6">
                                            <div className="p-6 bg-gray-700/30 rounded-xl border border-gray-600/30">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center space-x-4">
                                                        <div className="w-10 h-10 bg-purple-600/20 rounded-lg flex items-center justify-center">
                                                            <Key className="w-5 h-5 text-purple-400" />
                                                        </div>
                                                        <div>
                                                            <h3 className="font-semibold text-white text-lg">Password</h3>
                                                            <p className="text-sm text-gray-400">Last updated 3 months ago</p>
                                                        </div>
                                                    </div>
                                                    <button
                                                        onClick={handleChangePassword}
                                                        className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl transition-all duration-200 font-medium shadow-lg hover:shadow-purple-500/25"
                                                    >
                                                        Change Password
                                                    </button>
                                                </div>
                                            </div>
                                            <div className="p-6 bg-gray-700/30 rounded-xl border border-gray-600/30">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center space-x-4">
                                                        <div className="w-10 h-10 bg-green-600/20 rounded-lg flex items-center justify-center">
                                                            <Shield className="w-5 h-5 text-green-400" />
                                                        </div>
                                                        <div>
                                                            <h3 className="font-semibold text-white text-lg">Two-Factor Authentication</h3>
                                                            <p className="text-sm text-gray-400">Add an extra layer of security</p>
                                                        </div>
                                                    </div>
                                                    <button className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-xl transition-all duration-200 font-medium">
                                                        Enable 2FA
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </AuthGuard>
    );
}