'use client'

import { useEffect, useState } from 'react'
import { videoApi } from '@/lib/api'
import { Loader2 } from 'lucide-react'

interface ProcessingStatusProps {
    taskId: string
    onComplete: () => void
}

export default function ProcessingStatus({ taskId, onComplete }: ProcessingStatusProps) {
    const [status, setStatus] = useState<string>('Initializing...')
    const [progress, setProgress] = useState(0)

    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                const response = await videoApi.get(`/videos/${taskId}`)
                const { status: videoStatus, clips_count } = response.data

                // Map backend status to UI messages
                if (videoStatus === 'finished') {
                    setProgress(100)
                    setStatus('✨ Analysis Complete!')
                    clearInterval(interval)
                    setTimeout(onComplete, 1000)
                } else if (videoStatus === 'error') {
                    setStatus('❌ Processing failed')
                    clearInterval(interval)
                } else if (videoStatus === 'processing') {
                    // Simulate progress based on time
                    setProgress((prev) => {
                        if (prev < 30) return prev + 5; // Fast start
                        if (prev < 70) return prev + 2; // Analysis phase
                        if (prev < 90) return prev + 0.5; // Finalizing
                        return prev;
                    })

                    // Cycle through messages based on progress
                    if (progress < 30) setStatus('🎙️ Downloading and extracting audio...');
                    else if (progress < 60) setStatus('🧠 AI analyzing viral potential...');
                    else if (progress < 80) setStatus('✂️ Generating clips...');
                    else setStatus('✨ Finalizing...');
                } else {
                    setStatus('⏳ Queued for processing...')
                }
            } catch (error) {
                console.error('Failed to fetch status:', error)
            }
        }, 2000)

        return () => clearInterval(interval)
    }, [taskId, onComplete, progress])

    return (
        <div className="p-8 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 text-center">
            <Loader2 className="w-16 h-16 text-purple-500 animate-spin mx-auto mb-4" />

            <h3 className="text-2xl font-bold text-white mb-2">Processing Your Video</h3>
            <p className="text-gray-400 mb-6">{status}</p>

            {/* Progress Bar */}
            <div className="w-full bg-white/10 rounded-full h-3 mb-4 overflow-hidden">
                <div
                    className="h-full bg-gradient-to-r from-purple-600 to-pink-600 transition-all duration-500"
                    style={{ width: `${progress}%` }}
                />
            </div>

            <p className="text-sm text-gray-500">
                This may take a few minutes depending on video length
            </p>
        </div>
    )
}
