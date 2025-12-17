'use client'

import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { videoApi } from '@/lib/api'
import { Video as VideoIcon, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { format } from 'date-fns'

interface Video {
    id: number
    filename: string
    duration: number
    status: string
    created_at: string
    clips_count: number
}

export default function DashboardPage() {
    const { data: videos, isLoading, refetch } = useQuery({
        queryKey: ['videos'],
        queryFn: async () => {
            const response = await videoApi.get('/videos')
            return response.data
        },
    })

    const handleDeleteVideo = async (id: number) => {
        try {
            await videoApi.delete(`/videos/${id}`)
            refetch()
        } catch (error) {
            console.error('Failed to delete video:', error)
            alert('Failed to delete video')
        }
    }

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-4xl font-bold text-white mb-2">My Videos</h1>
                <p className="text-gray-400">View and manage your processed videos</p>
            </div>

            {isLoading ? (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-64 bg-white/5 rounded-xl animate-pulse" />
                    ))}
                </div>
            ) : videos?.length === 0 ? (
                <div className="text-center py-20">
                    <VideoIcon className="w-20 h-20 text-gray-600 mx-auto mb-4" />
                    <h3 className="text-2xl font-bold text-white mb-2">No videos yet</h3>
                    <p className="text-gray-400 mb-6">Upload your first video to get started!</p>
                    <Link
                        href="/dashboard/upload"
                        className="inline-block px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-semibold transition"
                    >
                        Upload Video
                    </Link>
                </div>
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {videos?.map((video: Video) => (
                        <VideoCard key={video.id} video={video} onDelete={handleDeleteVideo} />
                    ))}
                </div>
            )}
        </div>
    )
}

function VideoCard({ video, onDelete }: { video: Video; onDelete: (id: number) => void }) {
    const statusConfig = {
        uploaded: { icon: Clock, color: 'text-blue-400', label: 'Uploaded' },
        processing: { icon: Clock, color: 'text-yellow-400', label: 'Processing' },
        finished: { icon: CheckCircle, color: 'text-green-400', label: 'Ready' },
        error: { icon: AlertCircle, color: 'text-red-400', label: 'Error' },
    }

    const config = statusConfig[video.status as keyof typeof statusConfig] || statusConfig.uploaded
    const StatusIcon = config.icon

    const handleDelete = (e: React.MouseEvent) => {
        e.preventDefault() // Prevent navigation
        e.stopPropagation()
        if (confirm('Are you sure you want to delete this video?')) {
            onDelete(video.id)
        }
    }

    return (
        <Link href={`/dashboard/videos/${video.id}`}>
            <div className="p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:border-purple-500/50 transition cursor-pointer relative group">
                <button
                    onClick={handleDelete}
                    className="absolute top-4 right-4 p-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity z-10"
                    title="Delete video"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18" /><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" /><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" /></svg>
                </button>

                <div className="flex items-start justify-between mb-4">
                    <VideoIcon className="w-10 h-10 text-purple-400" />
                    <div className={`flex items-center gap-1 ${config.color}`}>
                        <StatusIcon className="w-5 h-5" />
                        <span className="text-sm font-semibold">{config.label}</span>
                    </div>
                </div>

                <h3 className="text-lg font-semibold text-white mb-2 truncate pr-8">
                    {video.filename}
                </h3>

                <div className="space-y-1 text-sm text-gray-400">
                    {video.duration && (
                        <p>Duration: {Math.round(video.duration)}s</p>
                    )}
                    <p>Clips: {video.clips_count}</p>
                    <p>Uploaded: {format(new Date(video.created_at), 'MMM d, yyyy')}</p>
                </div>
            </div>
        </Link>
    )
}
