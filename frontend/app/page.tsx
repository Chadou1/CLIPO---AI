import Link from 'next/link'
import { Sparkles, Zap, Video, TrendingUp } from 'lucide-react'

export default function HomePage() {
    return (
        <main className="min-h-screen bg-gradient-to-br from-gray-950 via-purple-950 to-gray-950">
            {/* Navigation */}
            <nav className="container mx-auto px-6 py-6 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <Video className="w-8 h-8 text-purple-500" />
                    <span className="text-2xl font-bold text-white">Clipo</span>
                </div>
                <div className="flex gap-4">
                    <Link href="/login" className="px-6 py-2 text-white hover:text-purple-400 transition">
                        Login
                    </Link>
                    <Link href="/register" className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition">
                        Get Started
                    </Link>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="container mx-auto px-6 py-20 text-center">
                <div className="animate-fade-in">
                    <h1 className="text-6xl md:text-7xl font-bold text-white mb-6">
                        Turn Videos Into
                        <br />
                        <span className="bg-gradient-to-r from-purple-400 to-pink-600 text-transparent bg-clip-text">
                            Viral Clips
                        </span>
                    </h1>
                    <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
                        AI-powered video editing that finds the best moments, adds subtitles, and reframes for TikTok & Reels
                    </p>
                    <div className="flex gap-4 justify-center">
                        <Link href="/register" className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-semibold text-lg transition transform hover:scale-105">
                            Start Free Trial
                        </Link>
                        <Link href="/pricing" className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white rounded-lg font-semibold text-lg transition backdrop-blur-sm">
                            View Pricing
                        </Link>
                    </div>
                </div>
            </section>

            {/* Features */}
            <section className="container mx-auto px-6 py-20">
                <h2 className="text-4xl font-bold text-white text-center mb-16">
                    Powered by AI, Built for Creators
                </h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                    <FeatureCard
                        icon={<Sparkles className="w-12 h-12 text-purple-400" />}
                        title="AI Viral Detection"
                        description="Our AI analyzes your video to find the most engaging moments automatically"
                    />
                    <FeatureCard
                        icon={<Video className="w-12 h-12 text-pink-400" />}
                        title="Auto Reframing"
                        description="Smart face tracking and 9:16 crop for perfect vertical videos"
                    />
                    <FeatureCard
                        icon={<Zap className="w-12 h-12 text-yellow-400" />}
                        title="Animated Subtitles"
                        description="TikTok-style captions with emojis, auto-generated and synced"
                    />
                    <FeatureCard
                        icon={<TrendingUp className="w-12 h-12 text-green-400" />}
                        title="Viral Score"
                        description="Each clip gets a viral potential score to help you choose the best"
                    />
                </div>
            </section>

            {/* How It Works */}
            <section className="container mx-auto px-6 py-20 bg-white/5 backdrop-blur-sm rounded-3xl">
                <h2 className="text-4xl font-bold text-white text-center mb-16">
                    How It Works
                </h2>
                <div className="grid md:grid-cols-3 gap-12">
                    <Step number="1" title="Upload Video" description="Drag and drop your long-form video (podcast, YouTube, etc.)" />
                    <Step number="2" title="AI Processing" description="Our AI analyzes, cuts, and adds effects automatically" />
                    <Step number="3" title="Export & Share" description="Download your viral clips ready to post!" />
                </div>
            </section>

            {/* CTA */}
            <section className="container mx-auto px-6 py-20 text-center">
                <h2 className="text-5xl font-bold text-white mb-6">
                    Ready to Go Viral?
                </h2>
                <p className="text-xl text-gray-300 mb-8">
                    Join thousands of creators using Clipo
                </p>
                <Link href="/register" className="inline-block px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-semibold text-lg transition transform hover:scale-105">
                    Get Started Free
                </Link>
            </section>

            {/* Footer */}
            <footer className="container mx-auto px-6 py-8 border-t border-gray-800 text-center text-gray-500">
                <p>© 2025 Clipo. All rights reserved.</p>
                <div className="mt-2 space-y-1">
                    <p>Create by chadou</p>
                    <p>contact at : chadou.pro1@gmail.com</p>
                </div>
            </footer>
        </main>
    )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
    return (
        <div className="p-6 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:border-purple-500/50 transition">
            <div className="mb-4">{icon}</div>
            <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
            <p className="text-gray-400">{description}</p>
        </div>
    )
}

function Step({ number, title, description }: { number: string, title: string, description: string }) {
    return (
        <div className="text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                {number}
            </div>
            <h3 className="text-2xl font-semibold text-white mb-2">{title}</h3>
            <p className="text-gray-400">{description}</p>
        </div>
    )
}
