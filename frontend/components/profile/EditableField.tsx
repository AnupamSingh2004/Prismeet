'use client';
import React from 'react';
import { Edit2, Save, X, Check, Loader2 } from 'lucide-react';
import { SelectOption } from '@/types/user';

interface EditableFieldProps {
    field: string;
    value: string | number;
    displayValue?: React.ReactNode;
    type?: string;
    placeholder?: string;
    icon?: React.ComponentType<{ className?: string }>;
    options?: SelectOption[];
    multiline?: boolean;
    className?: string;
    isEditing: boolean;
    isSaving: boolean;
    isSaved: boolean;
    onEdit: (field: string) => void;
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
    onSave: (field: string) => void;
    onCancel: (field: string) => void;
}

export const EditableField: React.FC<EditableFieldProps> = ({
                                                                field,
                                                                value,
                                                                displayValue,
                                                                type = 'text',
                                                                placeholder,
                                                                icon: Icon,
                                                                options,
                                                                multiline = false,
                                                                className = "",
                                                                isEditing,
                                                                isSaving,
                                                                isSaved,
                                                                onEdit,
                                                                onChange,
                                                                onSave,
                                                                onCancel
                                                            }) => {
    return (
        <div className={`group relative ${className}`}>
            {isEditing ? (
                <div className="space-y-3">
                    {multiline ? (
                        <textarea
                            name={field}
                            value={value}
                            onChange={onChange}
                            placeholder={placeholder}
                            rows={4}
                            className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white placeholder-gray-400 resize-none transition-all"
                            autoFocus
                        />
                    ) : options ? (
                        <select
                            name={field}
                            value={value}
                            onChange={onChange}
                            className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white transition-all"
                            autoFocus
                        >
                            {options.map(option => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    ) : (
                        <input
                            type={type}
                            name={field}
                            value={value}
                            onChange={onChange}
                            placeholder={placeholder}
                            className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white placeholder-gray-400 transition-all"
                            autoFocus
                        />
                    )}
                    <div className="flex items-center space-x-2">
                        <button
                            onClick={() => onSave(field)}
                            disabled={isSaving}
                            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white text-sm font-medium transition-colors flex items-center space-x-2 disabled:opacity-50"
                        >
                            {isSaving ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                                <Save className="w-4 h-4" />
                            )}
                            <span>{isSaving ? 'Saving...' : 'Save'}</span>
                        </button>
                        <button
                            onClick={() => onCancel(field)}
                            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white text-sm font-medium transition-colors flex items-center space-x-2"
                        >
                            <X className="w-4 h-4" />
                            <span>Cancel</span>
                        </button>
                    </div>
                </div>
            ) : (
                <div className="flex items-start justify-between group">
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                        {Icon && <Icon className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />}
                        <div className="flex-1 min-w-0">
                            <div className="text-gray-200 break-words">
                                {displayValue || value || (
                                    <span className="text-gray-500 italic">
                                        {placeholder}
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity ml-3 flex-shrink-0">
                        {isSaved && (
                            <div className="flex items-center space-x-1 text-green-400 text-sm">
                                <Check className="w-4 h-4" />
                                <span>Saved</span>
                            </div>
                        )}
                        <button
                            onClick={() => onEdit(field)}
                            className="p-2 hover:bg-gray-700/50 rounded-lg transition-colors"
                        >
                            <Edit2 className="w-4 h-4 text-gray-400" />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};