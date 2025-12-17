'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { Film, Download, Sparkles, AlertCircle } from 'lucide-react'
import { format } from 'date-fns'

const LIBRARY_API_URL = process.env.NEXT_PUBLIC_LIBRARY_API_URL || 'http://localhost:32189'

interface LibraryClip {
    filename: string
    url: string
    created_at: string
    size?: number
}

export default function LibraryClipsPage() {
    const router = useRouter()
    const [clips, setClips] = useState<LibraryClip[]>([])

    // Note: Since library service doesn't have a clips listing endpoint yet,
    // we'll need to implement this or show files from the output directory
    const { data: userInfo } = useQuery({
        queryKey: ['userInfo'],
        queryFn: async () => {
            const token = localStorage.getItem('token')
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/me`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            if (!response.ok) throw new Error('Failed to fetch user info')
            return response.json()
        }
    })

    // For now, we'll show a placeholder. In production, you'd implement
    // an endpoint to list generated library clips
    const hasClips = clips.length > 0

    return (
        <div>
            <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h1 className="text-4xl font-bold text-white mb-2">Library Generated Clips</h1>
                        <p className="text-gray-400">View and download your generated clips</p>
                    </div>
                    <button
                        onClick={() => router.push('/dashboard/library')}
                        className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition flex items-center gap-2"
                    >
                        <Sparkles className="w-5 h-5" />
                        Generate New Clip
                    </button>
                </div>

                {userInfo && (
                    <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg mb-6">
                        <div className="flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-blue-400 mt-0.5" />
                            <div>
                                <p className="text-blue-400 font-semibold">Credits: {userInfo.credits}</p>
                                <p className="text-gray-400 text-sm mt-1">
                                    Generated clips are stored in the library output directory
                                </p>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {!hasClips ? (
                <div className="text-center py-20">
                    <Film className="w-20 h-20 text-gray-600 mx-auto mb-4" />
                    <h3 className="text-2xl font-bold text-white mb-2">No clips generated yet</h3>
                    <p className="text-gray-400 mb-6">
                        Create your first library clip to see it here!
                    </p>
                    <button
                        onClick={() => router.push('/dashboard/library')}
                        className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-semibold transition"
                    >
                        <Sparkles className="w-5 h-5" />
                        Generate Your First Clip
                    </button>
                </div>
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {clips.map((clip, index) => (
                        <ClipCard key={index} clip={clip} />
                    ))}
                </div>
            )}

            {/* Info Panel */}
            <div className="mt-8 p-6 bg-gray-800/50 backdrop-blur-sm rounded-xl border border-white/10">
                <h3 className="text-white font-semibold mb-3">📂 Clip Storage Location</h3>
                <p className="text-gray-400 text-sm mb-2">
                    Generated clips are saved to:
                </p>
                <code className="block px-4 py-2 bg-black/50 text-green-400 rounded-lg text-sm font-mono">
                    D:\SITES\clipgenius\backend\storage\library_output\
                </code>
                <p className="text-gray-400 text-sm mt-3">
                    You can access these files directly from your file system.
                </p>
            </div>
        </div>
    )
}

function ClipCard({ clip }: { clip: LibraryClip }) {
    const handleDownload = () => {
        window.open(clip.url, '_blank')
    }

    return (
        <div className="p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:border-purple-500/50 transition">
            <div className="flex items-start justify-between mb-4">
                <Film className="w-10 h-10 text-purple-400" />
                <button
                    onClick={handleDownload}
                    className="p-2 bg-purple-600/20 hover:bg-purple-600/30 text-purple-400 rounded-full transition"
                    title="Download clip"
                >
                    <Download className="w-5 h-5" />
                </button>
            </div>

            <h3 className="text-lg font-semibold text-white mb-2 truncate">
                {clip.filename}
            </h3>

            <div className="space-y-1 text-sm text-gray-400">
                {clip.size && (
                    <p>Size: {(clip.size / 1024 / 1024).toFixed(2)} MB</p>
                )}
                <p>Created: {format(new Date(clip.created_at), 'MMM d, yyyy HH:mm')}</p>
            </div>
        </div>
    )
}
