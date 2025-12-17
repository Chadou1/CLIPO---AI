'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store'
import { Video, LogOut, Coins, Upload, Key } from 'lucide-react'

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const router = useRouter()
    const { user, isAuthenticated, logout } = useAuthStore()

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login')
        }
    }, [isAuthenticated, router])

    if (!isAuthenticated) return null

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-950 via-purple-950 to-gray-950">
            {/* Navigation */}
            <nav className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
                <div className="container mx-auto px-6 py-4 flex justify-between items-center">
                    <Link href="/dashboard" className="flex items-center gap-2">
                        <Video className="w-8 h-8 text-purple-500" />
                        <span className="text-2xl font-bold text-white">Clipo</span>
                    </Link>

                    <div className="flex items-center gap-6">
                        {/* Credits */}
                        <div className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-lg">
                            <Coins className="w-5 h-5 text-yellow-400" />
                            <span className="text-white font-semibold">{user?.credits || 0} crédits</span>
                        </div>

                        {/* Plan Badge */}
                        <div className="px-4 py-2 bg-purple-600/20 border border-purple-500 rounded-lg">
                            <span className="text-purple-300 font-semibold capitalize">{user?.plan || 'free'}</span>
                        </div>

                        {/* Upgrade Button (if FREE plan) */}
                        {user?.plan === 'free' && (
                            <Link
                                href="/dashboard/upgrade"
                                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-700 hover:to-orange-700 text-white rounded-lg font-semibold transition"
                            >
                                <Coins className="w-5 h-5" />
                                Upgrade to PRO
                            </Link>
                        )}

                        {/* Library Button */}
                        <Link
                            href="/dashboard/library"
                            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white rounded-lg font-semibold transition"
                        >
                            <Video className="w-5 h-5" />
                            Bibliothèque
                        </Link>

                        {/* Upload Button */}
                        <Link
                            href="/dashboard/upload"
                            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-semibold transition"
                        >
                            <Upload className="w-5 h-5" />
                            Upload
                        </Link>

                        {/* Logout */}
                        <button
                            onClick={logout}
                            className="p-2 text-gray-400 hover:text-white transition"
                            title="Déconnexion"
                        >
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="container mx-auto px-6 py-8">
                {children}
            </main>
        </div>
    )
}
