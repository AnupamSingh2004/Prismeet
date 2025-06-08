'use client';
import React from 'react';
import { User, Calendar, Bell, Shield, LucideIcon } from 'lucide-react';

interface Tab {
    id: string;
    label: string;
    icon: LucideIcon;
}

interface ProfileNavigationProps {
    activeTab: string;
    onTabChange: (tabId: string) => void;
}

export const ProfileNavigation: React.FC<ProfileNavigationProps> = ({
                                                                        activeTab,
                                                                        onTabChange
                                                                    }) => {
    const tabs: Tab[] = [
        { id: 'profile', label: 'Profile', icon: User },
        { id: 'meetings', label: 'Meetings', icon: Calendar },
        { id: 'notifications', label: 'Notifications', icon: Bell },
        { id: 'security', label: 'Security', icon: Shield }
    ];

    return (
        <nav className="space-y-2">
            {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;

                return (
                    <button
                        key={tab.id}
                        onClick={() => onTabChange(tab.id)}
                        className={`w-full flex items-center space-x-3 px-4 py-3 text-left rounded-xl transition-all duration-200 ${
                            isActive
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
    );
};