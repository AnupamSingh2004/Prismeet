'use client';

import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import MeetingDashboard from '@/components/meeting/MeetingDashboard';
import { AuthGuard } from '@/components/auth/AuthGuard';

export default function DashboardPage() {
  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <MeetingDashboard />
        </div>
      </div>
    </AuthGuard>
  );
}

