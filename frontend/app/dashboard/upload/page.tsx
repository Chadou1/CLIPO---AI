'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { videoApi } from '@/lib/api'
import VideoUpload from '@/components/VideoUpload'
import ProcessingStatus from '@/components/ProcessingStatus'
import { toast } from 'sonner'

export default function UploadPage() {
    const router = useRouter()
    const [uploading, setUploading] = useState(false)
    const [processing, setProcessing] = useState(false)
    const [taskId, setTaskId] = useState<string | null>(null)

    const handleUpload = async (url: string, quality?: string, fps?: number) => {
        setUploading(true)

        try {
            const uploadResponse = await videoApi.post('/videos/upload', {
                url,
                quality,
                fps
            })

            const videoId = uploadResponse.data.id
            toast.success('Video queued for processing!')

            // Start processing (actually just tracking status now since it's auto-started)
            setTaskId(videoId.toString())
            setProcessing(true)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Processing failed')
        } finally {
            setUploading(false)
        }
    }

    const handleProcessingComplete = () => {
        toast.success('Your clips are ready!')
        router.push('/dashboard')
    }

    return (
        <div className="max-w-3xl mx-auto">
            <div className="mb-8">
                <h1 className="text-4xl font-bold text-white mb-2">Upload Video</h1>
                <p className="text-gray-400">Upload your video and let AI create viral clips</p>
            </div>

            {processing && taskId ? (
                <ProcessingStatus taskId={taskId} onComplete={handleProcessingComplete} />
            ) : (
                <VideoUpload onUpload={handleUpload} loading={uploading} />
            )}
        </div>
    )
}
