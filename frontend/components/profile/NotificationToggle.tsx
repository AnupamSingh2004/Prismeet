'use client';
import React from 'react';
import { Check, Loader2 } from 'lucide-react';

interface NotificationToggleProps {
    field: string;
    checked: boolean;
    label: string;
    description: string;
    isSaving: boolean;
    isSaved: boolean;
    onToggle: (field: string) => void;
}

export const NotificationToggle: React.FC<NotificationToggleProps> = ({
                                                                          field,
                                                                          checked,
                                                                          label,
                                                                          description,
                                                                          isSaving,
                                                                          isSaved,
                                                                          onToggle
                                                                      }) => {
    return (
        <div className="flex items-center justify-between p-4 bg-gray-800/30 rounded-xl border border-gray-700/50 hover:border-gray-600/50 transition-colors">
            <div className="flex-1 min-w-0 pr-4">
                <div className="flex items-center space-x-3">
                    <h4 className="text-white font-medium">{label}</h4>
                    {isSaved && (
                        <div className="flex items-center space-x-1 text-green-400 text-sm">
                            <Check className="w-3 h-3" />
                            <span>Saved</span>
                        </div>
                    )}
                </div>
                <p className="text-gray-400 text-sm mt-1">{description}</p>
            </div>
            <button
                onClick={() => onToggle(field)}
                disabled={isSaving}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-900 disabled:opacity-50 flex-shrink-0 ${
                    checked ? 'bg-purple-600' : 'bg-gray-600'
                }`}
            >
                <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        checked ? 'translate-x-6' : 'translate-x-1'
                    }`}
                />
                {isSaving && (
                    <Loader2 className="absolute inset-0 w-4 h-4 m-auto animate-spin text-white" />
                )}
            </button>
        </div>
    );
};