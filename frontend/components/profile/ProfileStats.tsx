'use client';

import React from 'react';
import { Calendar, PlayCircle, Users, Award } from 'lucide-react';
import { StatItem } from '@/types/user';

const stats: StatItem[] = [
    { icon: Calendar, value: '127', label: 'Meetings Hosted', color: 'purple' },
    { icon: PlayCircle, value: '89', label: 'Hours Recorded', color: 'blue' },
    { icon: Users, value: '24', label: 'Team Members', color: 'green' },
    { icon: Award, value: '12', label: 'Achievements', color: 'yellow' }
];

export const ProfileStats: React.FC = () => {
    return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {stats.map((stat, index) => (
                <div key={index} className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50 text-center hover:bg-gray-800/70 transition-all">
                    <div className={`w-12 h-12 mx-auto mb-3 rounded-xl bg-${stat.color}-500/20 flex items-center justify-center`}>
                        <stat.icon className={`w-6 h-6 text-${stat.color}-400`} />
                    </div>
                    <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
                    <div className="text-sm text-gray-400">{stat.label}</div>
                </div>
            ))}
        </div>
    );
};