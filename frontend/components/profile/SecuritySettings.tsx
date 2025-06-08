'use client';
import React from 'react';
import { Key, Shield } from 'lucide-react';

interface SecuritySettingsProps {
    onChangePassword: () => void;
}

export const SecuritySettings: React.FC<SecuritySettingsProps> = ({
                                                                      onChangePassword
                                                                  }) => {
    const handleEnable2FA = () => {
        // TODO: Implement 2FA setup
        console.log('Enable 2FA clicked');
    };

    return (
        <div className="space-y-6">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700/30 p-8 shadow-xl">
                <h2 className="text-xl font-semibold text-white mb-8">Security Settings</h2>
                <div className="space-y-6">
                    {/* Password Section */}
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
                                onClick={onChangePassword}
                                className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl transition-all duration-200 font-medium shadow-lg hover:shadow-purple-500/25"
                            >
                                Change Password
                            </button>
                        </div>
                    </div>

                    {/* 2FA Section */}
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
                            <button
                                onClick={handleEnable2FA}
                                className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-xl transition-all duration-200 font-medium"
                            >
                                Enable 2FA
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};