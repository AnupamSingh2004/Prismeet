'use client'

import React, { useState, useEffect, useRef } from 'react';
import { Bell, LogOut, User, Video, Calendar, FileText, Menu, X } from 'lucide-react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

import { useAuth } from '@/hooks/useAuth';

const Navbar = () => {
    const { user, logout, isAuthenticated } = useAuth();
    const [isProfileOpen, setIsProfileOpen] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const profileDropdownRef = useRef<HTMLDivElement>(null);
    const router = useRouter();

    const navItems = [
        { name: 'Dashboard', href: '/dashboard', icon: Video },
        { name: 'Meetings', href: '/meeting', icon: Calendar },
        { name: 'Recordings', href: '/recordings', icon: FileText },
    ];

    // Handle clicks outside profile dropdown
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (profileDropdownRef.current && !profileDropdownRef.current.contains(event.target as Node)) {
                setIsProfileOpen(false);
            }
        };

        if (isProfileOpen) {
            document.addEventListener('mousedown', handleClickOutside);
            return () => {
                document.removeEventListener('mousedown', handleClickOutside);
            };
        }
    }, [isProfileOpen]);

    const handleLogout = () => {
        logout();
        router.push('/');
    };

    const handleLogoClick = () => {
        router.push('/');
    };

    const handleProfileSettingsClick = () => {
        router.push('/profile');
        setIsProfileOpen(false);
    };

    const ProfileDropdown = () => (
        <div
            ref={profileDropdownRef}
            className="absolute right-0 top-full mt-2 w-64 bg-gray-900/95 backdrop-blur-xl border border-gray-700/50 rounded-2xl shadow-2xl z-50 overflow-hidden"
        >
            <div className="p-4 border-b border-gray-700/50">
                <div className="flex items-center space-x-3">
                    {user?.profile_picture ? (
                        <div className="w-12 h-12 rounded-full overflow-hidden relative">
                            <Image
                                src={user.profile_picture}
                                alt={user.full_name || 'User'}
                                fill
                                className="object-cover"
                                sizes="48px"
                            />
                        </div>
                    ) : (
                        <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-semibold text-lg">
                            {user?.first_name && user?.last_name
                                ? `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
                                : user?.full_name
                                    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
                                    : 'U'
                            }
                        </div>
                    )}
                    <div className="flex-1 min-w-0">
                        <p className="font-semibold text-white truncate">
                            {user?.full_name || `${user?.first_name || ''} ${user?.last_name || ''}`.trim() || 'User'}
                        </p>
                        <p className="text-sm text-gray-400 truncate">{user?.email || 'user@example.com'}</p>
                    </div>
                </div>
            </div>

            <div className="p-2">
                <button
                    onClick={handleProfileSettingsClick}
                    className="w-full flex items-center space-x-3 px-3 py-2 text-gray-300 hover:bg-gray-800/50 rounded-lg transition-colors"
                >
                    <User className="w-4 h-4" />
                    <span>Profile Settings</span>
                </button>
                <hr className="my-2 border-gray-700/50" />
                <button
                    onClick={handleLogout}
                    className="w-full flex items-center space-x-3 px-3 py-2 text-red-400 hover:bg-red-900/20 rounded-lg transition-colors"
                >
                    <LogOut className="w-4 h-4" />
                    <span>Sign Out</span>
                </button>
            </div>
        </div>
    );

    return (
        <nav className="sticky top-0 z-40 bg-gray-900/90 backdrop-blur-xl border-b border-gray-700/50 shadow-lg">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <div className="flex items-center space-x-4">
                        <button
                            onClick={handleLogoClick}
                            className="flex items-center space-x-2 hover:opacity-80 transition-opacity"
                        >
                            <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
                                <Video className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                                Prismeet
                            </span>
                        </button>
                    </div>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-1">
                        {navItems.map((item) => (
                            <a
                                key={item.name}
                                href={item.href}
                                className="flex items-center space-x-2 px-4 py-2 text-gray-300 hover:text-purple-400 hover:bg-gray-800/50 rounded-lg transition-all duration-200 group"
                            >
                                <item.icon className="w-4 h-4 group-hover:scale-110 transition-transform" />
                                <span className="font-medium">{item.name}</span>
                            </a>
                        ))}
                    </div>

                    {/* Right Side Actions */}
                    <div className="flex items-center space-x-3">
                        {/* Notifications */}
                        <button className="relative p-2 text-gray-400 hover:text-purple-400 hover:bg-gray-800/50 rounded-lg transition-colors">
                            <Bell className="w-5 h-5" />
                            <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full flex items-center justify-center">
                                <span className="w-1.5 h-1.5 bg-white rounded-full"></span>
                            </span>
                        </button>

                        {/* Profile */}
                        {isAuthenticated && (
                            <div className="relative">
                                <button
                                    onClick={() => setIsProfileOpen(!isProfileOpen)}
                                    className="flex items-center space-x-2 p-1.5 hover:bg-gray-800/50 rounded-lg transition-colors"
                                >
                                    {user?.profile_picture ? (
                                        <div className="w-8 h-8 rounded-full overflow-hidden relative">
                                            <Image
                                                src={user.profile_picture}
                                                alt={user.full_name || 'User'}
                                                fill
                                                className="object-cover"
                                                sizes="32px"
                                            />
                                        </div>
                                    ) : (
                                        <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                                            {user?.first_name && user?.last_name
                                                ? `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
                                                : user?.full_name
                                                    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
                                                    : 'U'
                                            }
                                        </div>
                                    )}
                                    <div className="hidden sm:block text-left">
                                        <p className="text-sm font-medium text-white">
                                            {user?.full_name || `${user?.first_name || ''} ${user?.last_name || ''}`.trim() || 'User'}
                                        </p>
                                    </div>
                                </button>
                                {isProfileOpen && <ProfileDropdown />}
                            </div>
                        )}

                        {/* Mobile Menu Button */}
                        <button
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            className="md:hidden p-2 text-gray-400 hover:text-purple-400 hover:bg-gray-800/50 rounded-lg transition-colors"
                        >
                            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {isMobileMenuOpen && (
                <div className="md:hidden bg-gray-900/95 backdrop-blur-xl border-t border-gray-700/50">
                    <div className="px-4 py-2 space-y-1">
                        {navItems.map((item) => (
                            <a
                                key={item.name}
                                href={item.href}
                                className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-purple-400 hover:bg-gray-800/50 rounded-lg transition-colors"
                            >
                                <item.icon className="w-4 h-4" />
                                <span className="font-medium">{item.name}</span>
                            </a>
                        ))}
                        <hr className="my-2 border-gray-700/50" />
                        <div className="px-3 py-2">
                            <div className="flex items-center space-x-3 mb-2">
                                {user?.profile_picture ? (
                                    <div className="w-8 h-8 rounded-full overflow-hidden relative">
                                        <Image
                                            src={user.profile_picture}
                                            alt={user.full_name || 'User'}
                                            fill
                                            className="object-cover"
                                            sizes="32px"
                                        />
                                    </div>
                                ) : (
                                    <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                                        {user?.first_name && user?.last_name
                                            ? `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
                                            : user?.full_name
                                                ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
                                                : 'U'
                                        }
                                    </div>
                                )}
                                <div>
                                    <p className="text-sm font-medium text-white">
                                        {user?.full_name || `${user?.first_name || ''} ${user?.last_name || ''}`.trim() || 'User'}
                                    </p>
                                    <p className="text-xs text-gray-400">{user?.email || 'user@example.com'}</p>
                                </div>
                            </div>
                            <button
                                onClick={handleLogout}
                                className="flex items-center space-x-2 w-full px-2 py-1.5 text-red-400 hover:bg-red-900/20 rounded-lg transition-colors text-sm"
                            >
                                <LogOut className="w-4 h-4" />
                                <span>Sign Out</span>
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navbar;