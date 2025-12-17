'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Film, Sparkles, AlertCircle } from 'lucide-react'

const LIBRARY_API_URL = process.env.NEXT_PUBLIC_LIBRARY_API_URL || 'http://localhost:32189'

interface GenerateRequest {
    text: string
    library: string
    font: number
    fps: number
    resolution: string
    black_white_intensity: number
    speed: number
    font_size: number
    url_song: string // REQUIRED
}

export default function LibraryGeneratePage() {
    const router = useRouter()
    const [formData, setFormData] = useState<GenerateRequest>({
        text: '',
        library: 'Keo',
        font: 1,
        fps: 30,
        resolution: '720p',
        black_white_intensity: 0,
        speed: 4,
        font_size: 48,
        url_song: ''  // YouTube URL required
    })

    // Fetch user info to determine tier
    const { data: userInfo } = useQuery({
        queryKey: ['userInfo'],
        queryFn: async () => {
            const token = localStorage.getItem('token')
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:32190'
            const response = await fetch(`${apiUrl}/auth/me`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            if (!response.ok) throw new Error('Failed to fetch user info')
            return response.json()
        }
    })

    // Fetch available libraries
    const { data: libraries, isError: isLibError, error: libError } = useQuery({
        queryKey: ['libraries'],
        queryFn: async () => {
            const token = localStorage.getItem('token')
            const response = await fetch(`${LIBRARY_API_URL}/library/libraries`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            if (!response.ok) {
                const text = await response.text()
                throw new Error(`Failed to fetch libraries: ${response.status} ${text}`)
            }
            return response.json()
        }
    })

    // Fetch available fonts
    const { data: fonts, isError: isFontError, error: fontError } = useQuery({
        queryKey: ['fonts'],
        queryFn: async () => {
            const token = localStorage.getItem('token')
            const response = await fetch(`${LIBRARY_API_URL}/library/fonts`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            if (!response.ok) {
                const text = await response.text()
                throw new Error(`Failed to fetch fonts: ${response.status} ${text}`)
            }
            return response.json()
        }
    })

    const generateMutation = useMutation({
        mutationFn: async (data: GenerateRequest) => {
            const token = localStorage.getItem('token')
            const response = await fetch(`${LIBRARY_API_URL}/library/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify(data)
            })
            if (!response.ok) {
                const error = await response.json()
                throw new Error(error.detail || 'Failed to generate video')
            }
            return response.json()
        },
        onSuccess: (data) => {
            alert(`Video generated successfully! ${data.credits_remaining} credits remaining.`)
            router.push('/dashboard/library/clips')
        },
        onError: (error: Error) => {
            alert(error.message)
        }
    })

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (!formData.text.trim()) {
            alert('Please enter text for your video')
            return
        }
        if (!formData.url_song || !formData.url_song.trim()) {
            alert('Please enter a YouTube URL for the music')
            return
        }
        generateMutation.mutate(formData)
    }

    // Determine available options based on user plan
    const plan = userInfo?.plan || 'free'
    const canChooseQuality = plan !== 'free'

    let resolutionOptions = ['720p']
    let fpsOptions = [30]

    if (plan === 'starter') {
        resolutionOptions = ['720p', '1080p']
        fpsOptions = [30, 60]
    } else if (plan === 'pro' || plan === 'agency') {
        resolutionOptions = ['720p', '1080p']
        fpsOptions = [30, 60]
    }

    return (
        <div className="max-w-4xl mx-auto">
            {/* Debug Info - Remove in production */}
            <div className="mb-4 p-2 bg-gray-800 rounded text-xs text-gray-400 font-mono">
                API: {LIBRARY_API_URL} | Auth: {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:32190'}
            </div>

            <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h1 className="text-4xl font-bold text-white mb-2">Library Clip Generator</h1>
                        <p className="text-gray-400">Generate custom videos from your library</p>
                    </div>
                    <button
                        onClick={() => router.push('/dashboard/library/clips')}
                        className="px-4 py-2 bg-purple-600/20 hover:bg-purple-600/30 text-purple-400 rounded-lg transition flex items-center gap-2"
                    >
                        <Film className="w-5 h-5" />
                        View Generated Clips
                    </button>
                </div>

                {userInfo && (
                    <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                        <div className="flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-blue-400 mt-0.5" />
                            <div>
                                <p className="text-blue-400 font-semibold">Plan: {plan.toUpperCase()} | Credits: {userInfo.credits}</p>
                                <p className="text-gray-400 text-sm mt-1">Each generation costs 1 credit</p>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Text Input */}
                <div className="p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10">
                    <label className="block text-white font-semibold mb-2">
                        Video Text *
                    </label>
                    <textarea
                        value={formData.text}
                        onChange={(e) => setFormData({ ...formData, text: e.target.value })}
                        className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition"
                        placeholder="Enter your text here... Use :ligne for line breaks"
                        rows={4}
                        maxLength={500}
                        required
                    />
                    <p className="text-gray-400 text-sm mt-2">{formData.text.length}/500 characters</p>
                </div>

                {/* Library Selection */}
                <div className="p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10">
                    <label className="block text-white font-semibold mb-2">
                        Video Library *
                    </label>
                    <select
                        value={formData.library}
                        onChange={(e) => setFormData({ ...formData, library: e.target.value })}
                        className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg text-white focus:outline-none focus:border-purple-500 transition"
                        required
                    >
                        {isLibError ? (
                            <option>Error: {libError?.message}</option>
                        ) : !libraries ? (
                            <option>Loading libraries...</option>
                        ) : libraries.libraries && libraries.libraries.length > 0 ? (
                            libraries.libraries.map((lib: string) => (
                                <option key={lib} value={lib}>{lib}</option>
                            ))
                        ) : (
                            <option>No libraries available</option>
                        )}
                    </select>
                    {isLibError && (
                        <p className="text-red-400 text-sm mt-2">❌ Error loading libraries: {libError?.message}</p>
                    )}
                </div>

                {/* YouTube Music URL (REQUIRED) */}
                <div className="p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10">
                    <label className="block text-white font-semibold mb-2">
                        YouTube Music URL *
                    </label>
                    <input
                        type="url"
                        value={formData.url_song || ''}
                        onChange={(e) => setFormData({ ...formData, url_song: e.target.value })}
                        className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition"
                        placeholder="https://youtube.com/watch?v=... (max 5 min)"
                        required
                    />
                    <p className="text-gray-400 text-sm mt-2">
                        Audio will be downloaded from YouTube and deleted after generation.
                    </p>
                </div>

                {/* Quality Settings */}
                <div className="p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10">
                    <h3 className="text-white font-semibold mb-4">Quality Settings</h3>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-gray-400 text-sm mb-2">Resolution</label>
                            <select
                                value={formData.resolution}
                                onChange={(e) => setFormData({ ...formData, resolution: e.target.value })}
                                className="w-full px-4 py-2 bg-black/50 border border-white/10 rounded-lg text-white focus:outline-none focus:border-purple-500 transition"
                                disabled={!canChooseQuality}
                            >
                                {resolutionOptions.map(res => (
                                    <option key={res} value={res}>{res}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-gray-400 text-sm mb-2">FPS</label>
                            <select
                                value={formData.fps}
                                onChange={(e) => setFormData({ ...formData, fps: parseInt(e.target.value) })}
                                className="w-full px-4 py-2 bg-black/50 border border-white/10 rounded-lg text-white focus:outline-none focus:border-purple-500 transition"
                                disabled={!canChooseQuality}
                            >
                                {fpsOptions.map(fps => (
                                    <option key={fps} value={fps}>{fps} FPS</option>
                                ))}
                            </select>
                        </div>
                    </div>
                    {!canChooseQuality && (
                        <p className="text-yellow-400 text-sm mt-2">Quality locked to 720p @ 30fps for free plan</p>
                    )}
                </div>

                {/* Customization */}
                <div className="p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10">
                    <h3 className="text-white font-semibold mb-4">Customization</h3>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-gray-400 text-sm mb-2">
                                Font Style *
                            </label>
                            <select
                                value={formData.font}
                                onChange={(e) => setFormData({ ...formData, font: parseInt(e.target.value) })}
                                className="w-full px-4 py-2 bg-black/50 border border-white/10 rounded-lg text-white focus:outline-none focus:border-purple-500 transition"
                                required
                            >
                                {isFontError ? (
                                    <option>Error loading fonts</option>
                                ) : !fonts ? (
                                    <option>Loading fonts...</option>
                                ) : fonts.fonts && fonts.fonts.length > 0 ? (
                                    fonts.fonts.map((font: any) => (
                                        <option key={font.id} value={font.id}>
                                            {font.id}. {font.name}
                                        </option>
                                    ))
                                ) : (
                                    <option>No fonts available</option>
                                )}
                            </select>
                            {fonts && (!fonts.fonts || fonts.fonts.length === 0) && (
                                <p className="text-red-400 text-xs mt-1">⚠️ No fonts found. Check service connection.</p>
                            )}
                            {fonts && fonts.fonts && fonts.fonts.length > 0 && (
                                <p className="text-gray-400 text-xs mt-1">Preview will show after generation</p>
                            )}
                        </div>

                        <div>
                            <label className="block text-gray-400 text-sm mb-2">
                                Font Size ({formData.font_size}px)
                            </label>
                            <input
                                type="range"
                                min="30"
                                max="80"
                                value={formData.font_size}
                                onChange={(e) => setFormData({ ...formData, font_size: parseInt(e.target.value) })}
                                className="w-full"
                            />
                        </div>

                        <div>
                            <label className="block text-gray-400 text-sm mb-2">
                                Black & White Intensity ({formData.black_white_intensity}%)
                            </label>
                            <input
                                type="range"
                                min="0"
                                max="100"
                                value={formData.black_white_intensity}
                                onChange={(e) => setFormData({ ...formData, black_white_intensity: parseInt(e.target.value) })}
                                className="w-full"
                            />
                        </div>

                        <div>
                            <label className="block text-gray-400 text-sm mb-2">
                                Speed - Clips per Second ({formData.speed})
                            </label>
                            <input
                                type="range"
                                min="1"
                                max="8"
                                value={formData.speed}
                                onChange={(e) => setFormData({ ...formData, speed: parseInt(e.target.value) })}
                                className="w-full"
                            />
                        </div>
                    </div>
                </div>

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={generateMutation.isPending || !formData.text.trim()}
                    className="w-full px-6 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition flex items-center justify-center gap-2"
                >
                    {generateMutation.isPending ? (
                        <>
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                            Generating...
                        </>
                    ) : (
                        <>
                            <Sparkles className="w-5 h-5" />
                            Generate Video (1 Credit)
                        </>
                    )}
                </button>
            </form>
        </div>
    )
}
