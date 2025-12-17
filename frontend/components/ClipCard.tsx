'use client'

import { TrendingUp, Clock, FileVideo, Play } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import dynamic from 'next/dynamic'

// Dynamically import ReactPlayer to reduce initial bundle
const ReactPlayer = dynamic(() => import('react-player/lazy'), { ssr: false })

interface Clip {
    id: number
    start_time: number
    end_time: number
    viral_score: number
    style: string
    transcript_segment: string
    download_url: string
}

interface ClipCardProps {
    clip: Clip
    onExport: (clipId: number) => void
    exporting?: boolean
}

export default function ClipCard({ clip, onExport, exporting }: ClipCardProps) {
    const duration = Math.round(clip.end_time - clip.start_time)
    const [isVisible, setIsVisible] = useState(false)
    const [shouldLoad, setShouldLoad] = useState(false)
    const cardRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (!cardRef.current) return

        // Intersection Observer to detect when card is in viewport
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        setIsVisible(true)
                        // Delay loading slightly to avoid loading all at once during scroll
                        const timeout = setTimeout(() => setShouldLoad(true), 100)
                        return () => clearTimeout(timeout)
                    } else {
                        setIsVisible(false)
                        // Unload video when it leaves viewport to free memory
                        setShouldLoad(false)
                    }
                })
            },
            {
                rootMargin: '200px', // Start loading 200px before entering viewport
                threshold: 0.1
            }
        )

        observer.observe(cardRef.current)

        return () => {
            if (cardRef.current) {
                observer.unobserve(cardRef.current)
            }
        }
    }, [])

    return (
        <div
            ref={cardRef}
            className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 overflow-hidden hover:border-purple-500/50 transition"
        >
            {/* Video Preview */}
            <div className="aspect-[9/16] bg-black relative">
                {clip.download_url && shouldLoad ? (
                    <ReactPlayer
                        url={clip.download_url}
                        width="100%"
                        height="100%"
                        controls
                        light={true}  // Show thumbnail, load on play
                        playing={false}
                        playIcon={
                            <div className="flex items-center justify-center w-16 h-16 bg-purple-600/80 backdrop-blur-sm rounded-full">
                                <Play className="w-8 h-8 text-white ml-1" fill="white" />
                            </div>
                        }
                        config={{
                            file: {
                                attributes: {
                                    preload: 'none',  // Don't preload until user clicks
                                    controlsList: 'nodownload',
                                }
                            }
                        }}
                    />
                ) : (
                    <div className="w-full h-full flex flex-col items-center justify-center gap-3">
                        <FileVideo className="w-16 h-16 text-gray-600" />
                        {!isVisible && (
                            <span className="text-gray-500 text-sm">Scroll to load</span>
                        )}
                    </div>
                )}

                {/* Viral Score Badge */}
                <div className="absolute top-3 right-3 px-3 py-1 bg-black/70 backdrop-blur-sm rounded-full flex items-center gap-1">
                    <TrendingUp className="w-4 h-4 text-green-400" />
                    <span className="text-white font-semibold text-sm">
                        {clip.viral_score?.toFixed(0) || 'N/A'}
                    </span>
                </div>
            </div>

            {/* Info */}
            <div className="p-4">
                <div className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                    <Clock className="w-4 h-4" />
                    <span>{duration}s</span>
                    <span className="ml-auto text-purple-400 capitalize">{clip.style}</span>
                </div>

                {clip.transcript_segment && (
                    <p className="text-gray-300 text-sm mb-4 line-clamp-3">
                        {clip.transcript_segment}
                    </p>
                )}

                <button
                    onClick={() => onExport(clip.id)}
                    disabled={exporting}
                    className="w-full py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {exporting ? 'Exporting...' : 'Export Clip (1 credit)'}
                </button>
            </div>
        </div>
    )
}
