'use client';
import React from 'react';
import { Mail, Check } from 'lucide-react';
import { User } from '@/types/user';

interface EmailFieldProps {
    user: User;
}

export const EmailField: React.FC<EmailFieldProps> = ({ user }) => {
    return (
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
    );
};