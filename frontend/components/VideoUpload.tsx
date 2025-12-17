'use client'

import { useState } from 'react'
import { Link as LinkIcon, Play, Settings, Monitor, Zap, Lock } from 'lucide-react'
import { useAuthStore } from '@/lib/store'

interface VideoUploadProps {
    onUpload: (url: string, quality?: string, fps?: number) => void
    loading?: boolean
}

export default function VideoUpload({ onUpload, loading }: VideoUploadProps) {
    const [url, setUrl] = useState('')
    const [quality, setQuality] = useState('720p')
    const [fps, setFps] = useState(30)

    const { user } = useAuthStore()
    const plan = user?.plan || 'free'

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (url) {
            onUpload(url, quality, fps)
        }
    }

    const QualityOption = ({ value, label, requiredPlan }: { value: string, label: string, requiredPlan?: string }) => {
        const isLocked = requiredPlan && plan === 'free' && requiredPlan !== 'free';
        // Logic for locking: 
        // Free: can only use 720p
        // Starter/Pro: can use 720p, 1080p
        // Agency: can use all

        let locked = false;
        if (value === '1080p' && plan === 'free') locked = true;
        if (value === '2k' && plan !== 'agency') locked = true;

        return (
            <button
                type="button"
                onClick={() => !locked && setQuality(value)}
                disabled={locked || loading}
                className={`relative flex flex-col items-center justify-center p-3 rounded-xl border transition-all ${quality === value
                        ? 'bg-purple-600/20 border-purple-500 text-white'
                        : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'
                    } ${locked ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
                {locked && <Lock className="absolute top-2 right-2 w-3 h-3 text-gray-500" />}
                <Monitor className={`w-6 h-6 mb-2 ${quality === value ? 'text-purple-400' : 'text-gray-500'}`} />
                <span className="text-sm font-medium">{label}</span>
            </button>
        )
    }

    const FpsOption = ({ value, label, requiredPlan }: { value: number, label: string, requiredPlan?: string }) => {
        let locked = false;
        if (value === 60 && plan !== 'agency') locked = true;

        return (
            <button
                type="button"
                onClick={() => !locked && setFps(value)}
                disabled={locked || loading}
                className={`relative flex flex-col items-center justify-center p-3 rounded-xl border transition-all ${fps === value
                        ? 'bg-pink-600/20 border-pink-500 text-white'
                        : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'
                    } ${locked ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
                {locked && <Lock className="absolute top-2 right-2 w-3 h-3 text-gray-500" />}
                <Zap className={`w-6 h-6 mb-2 ${fps === value ? 'text-pink-400' : 'text-gray-500'}`} />
                <span className="text-sm font-medium">{label}</span>
            </button>
        )
    }

    return (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-8 backdrop-blur-sm">
            <form onSubmit={handleSubmit} className="space-y-8">
                {/* URL Input */}
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                        YouTube Video URL
                    </label>
                    <div className="relative group">
                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <LinkIcon className="h-5 w-5 text-gray-500 group-focus-within:text-purple-500 transition-colors" />
                        </div>
                        <input
                            type="url"
                            required
                            placeholder="Paste YouTube URL here..."
                            className="block w-full pl-12 pr-4 py-4 border border-white/10 rounded-xl leading-5 bg-black/40 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            disabled={loading}
                        />
                    </div>
                </div>

                {/* Settings Grid */}
                <div className="grid md:grid-cols-2 gap-8">
                    {/* Quality Selection */}
                    <div className="space-y-3">
                        <label className="block text-sm font-medium text-gray-300">
                            Video Quality
                        </label>
                        <div className="grid grid-cols-3 gap-3">
                            <QualityOption value="720p" label="720p" />
                            <QualityOption value="1080p" label="1080p" />
                            <QualityOption value="2k" label="2K" />
                        </div>
                    </div>

                    {/* FPS Selection */}
                    <div className="space-y-3">
                        <label className="block text-sm font-medium text-gray-300">
                            Framerate
                        </label>
                        <div className="grid grid-cols-2 gap-3">
                            <FpsOption value={30} label="30 FPS" />
                            <FpsOption value={60} label="60 FPS" />
                        </div>
                    </div>
                </div>

                {/* Upgrade Prompt */}
                {plan === 'free' && (
                    <div className="p-4 bg-gradient-to-r from-purple-900/20 to-pink-900/20 border border-purple-500/20 rounded-xl text-center">
                        <p className="text-sm text-gray-300">
                            <span className="text-purple-400 font-semibold">Pro Tip:</span> Upgrade to unlock 1080p, 2K and 60 FPS processing!
                        </p>
                    </div>
                )}

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={loading || !url}
                    className={`w-full flex justify-center items-center py-4 px-6 border border-transparent rounded-xl shadow-lg text-base font-semibold text-white bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-all transform hover:scale-[1.02] active:scale-[0.98] ${loading ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                >
                    {loading ? (
                        <>
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-3" />
                            Processing Video...
                        </>
                    ) : (
                        <>
                            <Play className="w-5 h-5 mr-3 fill-current" />
                            Generate Viral Clips
                        </>
                    )}
                </button>
            </form>
        </div>
    )
}
