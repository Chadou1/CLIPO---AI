'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { useQuery, useMutation } from '@tanstack/react-query'
import { videoApi } from '@/lib/api'
import ClipCard from '@/components/ClipCard'
import { ArrowLeft, Edit2, Check, X } from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'

export default function VideoDetailPage() {
    const params = useParams()
    const videoId = params.id
    const [exportingClipId, setExportingClipId] = useState<number | null>(null)
    const [isRenaming, setIsRenaming] = useState(false)
    const [newName, setNewName] = useState('')

    const { data: video, isLoading: videoLoading, refetch: refetchVideo } = useQuery({
        queryKey: ['video', videoId],
        queryFn: async () => {
            const response = await videoApi.get(`/videos/${videoId}`)
            return response.data
        },
    })

    const { data: clips, isLoading: clipsLoading, refetch } = useQuery({
        queryKey: ['clips', videoId],
        queryFn: async () => {
            const response = await videoApi.get(`/videos/${videoId}/clips`)
            return response.data
        },
    })

    const exportMutation = useMutation({
        mutationFn: async (clipId: number) => {
            const response = await videoApi.post(`/clips/${clipId}/export`, {
                style: 'simple'
            })
            return response.data
        },
        onSuccess: (data, clipId) => {
            toast.success(`Clip exported! ${data.credits_remaining} credits remaining`)
            setExportingClipId(null)

            // Download clip
            const link = document.createElement('a')
            link.href = data.download_url
            link.download = `clip_${clipId}.mp4`
            link.click()
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'Export failed')
            setExportingClipId(null)
        },
    })

    const renameMutation = useMutation({
        mutationFn: async (name: string) => {
            const response = await videoApi.put(`/videos/${videoId}/rename`, {
                filename: name
            })
            return response.data
        },
        onSuccess: () => {
            toast.success('Video renamed successfully')
            setIsRenaming(false)
            refetchVideo()
        },
        onError: (error: any) => {
            toast.error('Failed to rename video')
        }
    })

    const handleExport = (clipId: number) => {
        setExportingClipId(clipId)
        exportMutation.mutate(clipId)
    }

    const handleRename = () => {
        if (newName.trim()) {
            renameMutation.mutate(newName)
        }
    }

    if (videoLoading) {
        return (
            <div className="flex items-center justify-center min-h-[50vh]">
                <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
            </div>
        )
    }

    return (
        <div>
            {/* Header */}
            <div className="mb-8">
                <Link href="/dashboard" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition mb-4">
                    <ArrowLeft className="w-5 h-5" />
                    Back to Dashboard
                </Link>

                <div className="flex items-center gap-4 mb-2">
                    {isRenaming ? (
                        <div className="flex items-center gap-2">
                            <input
                                type="text"
                                value={newName}
                                onChange={(e) => setNewName(e.target.value)}
                                className="bg-white/10 border border-white/20 rounded px-3 py-1 text-white text-2xl font-bold focus:outline-none focus:border-purple-500"
                                autoFocus
                            />
                            <button
                                onClick={handleRename}
                                className="p-2 bg-green-500/20 text-green-400 rounded hover:bg-green-500/30 transition"
                            >
                                <Check className="w-5 h-5" />
                            </button>
                            <button
                                onClick={() => setIsRenaming(false)}
                                className="p-2 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30 transition"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                    ) : (
                        <div className="flex items-center gap-2 group">
                            <h1 className="text-4xl font-bold text-white">{video?.filename}</h1>
                            <button
                                onClick={() => {
                                    setNewName(video?.filename || '')
                                    setIsRenaming(true)
                                }}
                                className="opacity-0 group-hover:opacity-100 p-2 text-gray-400 hover:text-white transition"
                            >
                                <Edit2 className="w-5 h-5" />
                            </button>
                        </div>
                    )}
                </div>

                <p className="text-gray-400">
                    {clips?.length || 0} clips generated
                </p>
            </div>

            {/* Clips Grid */}
            {clipsLoading ? (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-96 bg-white/5 rounded-xl animate-pulse" />
                    ))}
                </div>
            ) : clips?.length === 0 ? (
                <div className="text-center py-20 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10">
                    <h3 className="text-2xl font-bold text-white mb-2">No clips yet</h3>
                    <p className="text-gray-400">Clips are still being processed...</p>
                </div>
            ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {clips?.map((clip: any) => (
                        <ClipCard
                            key={clip.id}
                            clip={clip}
                            onExport={handleExport}
                            exporting={exportingClipId === clip.id}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}
