'use client'

import Link from 'next/link'
import { CheckCircle, Sparkles } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

export default function PaymentSuccessPage() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const [countdown, setCountdown] = useState(5)

    useEffect(() => {
        // Countdown timer
        const countdownInterval = setInterval(() => {
            setCountdown((prev) => {
                if (prev <= 1) {
                    clearInterval(countdownInterval)
                    router.push('/dashboard')
                    return 0
                }
                return prev - 1
            })
        }, 1000)

        return () => clearInterval(countdownInterval)
    }, [router])

    return (
        <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center p-4">
            <div className="max-w-md w-full bg-white/5 backdrop-blur-sm border border-green-500/30 rounded-2xl p-8 text-center relative overflow-hidden">
                {/* Animated background */}
                <div className="absolute inset-0 bg-gradient-to-r from-green-500/10 to-emerald-500/10 animate-pulse" />

                <div className="relative z-10">
                    <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6 animate-bounce">
                        <CheckCircle className="w-10 h-10 text-green-400" />
                    </div>

                    <div className="flex items-center justify-center gap-2 mb-4">
                        <Sparkles className="w-6 h-6 text-yellow-400" />
                        <h1 className="text-3xl font-bold text-white">Paiement réussi!</h1>
                        <Sparkles className="w-6 h-6 text-yellow-400" />
                    </div>

                    <p className="text-gray-400 mb-2">
                        Merci pour votre abonnement! Votre compte a été mis à jour.
                    </p>

                    <div className="bg-white/5 rounded-lg p-4 mb-8">
                        <p className="text-sm text-gray-300">
                            ✨ Vos crédits et fonctionnalités premium sont maintenant actifs
                        </p>
                    </div>

                    <Link
                        href="/dashboard"
                        className="inline-block w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 rounded-lg font-semibold transition mb-3"
                    >
                        Accéder au Dashboard
                    </Link>

                    <p className="text-sm text-gray-500">
                        Redirection automatique dans {countdown} seconde{countdown > 1 ? 's' : ''}...
                    </p>
                </div>
            </div>
        </div>
    )
}
