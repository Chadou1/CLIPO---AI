'use client'

import { useState, useEffect } from 'react'
import { Check, Zap, Crown, Rocket, ArrowLeft } from 'lucide-react'
import api from '@/lib/api'
import { useRouter } from 'next/navigation'

export default function PricingPage() {
    const [loading, setLoading] = useState<string | null>(null)
    const [plans, setPlans] = useState<any>(null)
    const router = useRouter()

    useEffect(() => {
        // Fetch plans from backend
        const fetchPlans = async () => {
            try {
                const response = await api.get('/payment/plans')
                setPlans(response.data.plans)
            } catch (error) {
                console.error('Error fetching plans:', error)
            }
        }
        fetchPlans()
    }, [])

    const handleSubscribe = async (plan: string) => {
        // For paid plans, redirect to login if not authenticated
        // User must be logged in to get email prefilled in Stripe checkout
        router.push('/login')
    }

    const pricingTiers = [
        {
            id: 'free',
            name: 'Free',
            icon: Zap,
            price: 0,
            period: 'Gratuit',
            description: 'Pour démarrer',
            features: [
                '3 vidéos gratuites',
                'Export 720p 30fps',
                'Analyse de score viral',
                'Support communautaire'
            ],
            color: 'from-gray-400 to-gray-600',
            borderColor: 'border-gray-500/30',
            popular: false
        },
        {
            id: 'starter',
            name: 'Starter',
            icon: Rocket,
            price: 9,
            period: '/mois',
            description: 'Pour les créateurs',
            features: plans?.starter?.features || [
                '10 vidéos par mois',
                'Export 1080p 30fps',
                'Analyse de score viral',
                'Support standard'
            ],
            color: 'from-blue-400 to-blue-600',
            borderColor: 'border-blue-500/30',
            popular: false
        },
        {
            id: 'pro',
            name: 'Pro',
            icon: Crown,
            price: 29,
            period: '/mois',
            description: 'Pour les professionnels',
            features: plans?.pro?.features || [
                '50 vidéos par mois',
                'Export 1080p 60fps',
                'Analyse de score viral',
                'Support prioritaire',
                'Pas de watermark'
            ],
            color: 'from-purple-400 to-pink-600',
            borderColor: 'border-purple-500/30',
            popular: true
        },
        {
            id: 'agency',
            name: 'Agency',
            icon: Zap,
            price: 89,
            period: '/mois',
            description: 'Pour les agences',
            features: plans?.agency?.features || [
                '200 vidéos par mois',
                'Export 2K/4K 60fps',
                'Traitement prioritaire',
                'Support dédié'
            ],
            color: 'from-yellow-400 to-orange-600',
            borderColor: 'border-yellow-500/30',
            popular: false
        }
    ]

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white py-20 px-4">
            {/* Back Button */}
            <div className="max-w-7xl mx-auto mb-8">
                <button
                    onClick={() => router.push('/')}
                    className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors group"
                >
                    <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                    <span>Retour à l'accueil</span>
                </button>
            </div>

            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="text-center mb-16">
                    <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-purple-400 via-pink-500 to-orange-500 bg-clip-text text-transparent">
                        Choisissez votre plan
                    </h1>
                    <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                        Des clips viraux générés par IA. Choisissez l'abonnement qui correspond à vos besoins.
                    </p>
                </div>

                {/* Pricing Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-4">
                    {pricingTiers.map((tier) => {
                        const Icon = tier.icon
                        return (
                            <div
                                key={tier.id}
                                className={`relative bg-white/5 backdrop-blur-sm border ${tier.borderColor} rounded-2xl p-6 transition-all duration-300 hover:scale-105 hover:shadow-2xl ${tier.popular ? 'ring-2 ring-purple-500 lg:scale-105' : ''
                                    }`}
                            >
                                {tier.popular && (
                                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs font-bold px-4 py-1 rounded-full">
                                        POPULAIRE
                                    </div>
                                )}

                                {/* Icon */}
                                <div className={`inline-flex p-3 mb-4 bg-gradient-to-r ${tier.color} rounded-xl`}>
                                    <Icon className="w-6 h-6 text-white" />
                                </div>

                                {/* Plan Name */}
                                <h3 className="text-2xl font-bold mb-2">{tier.name}</h3>
                                <p className="text-gray-400 text-sm mb-4">{tier.description}</p>

                                {/* Price */}
                                <div className="mb-6">
                                    <div className="flex items-baseline gap-1">
                                        <span className="text-4xl font-bold">${tier.price}</span>
                                        <span className="text-gray-400">{tier.period}</span>
                                    </div>
                                </div>

                                {/* Features */}
                                <ul className="space-y-3 mb-6">
                                    {tier.features.map((feature: string, i: number) => (
                                        <li key={i} className="flex items-start gap-2">
                                            <div className="p-0.5 bg-green-500/20 rounded-full mt-0.5">
                                                <Check className="w-3 h-3 text-green-400" />
                                            </div>
                                            <span className="text-sm text-gray-300">{feature}</span>
                                        </li>
                                    ))}
                                </ul>

                                {/* CTA Button */}
                                {tier.id === 'free' ? (
                                    <button
                                        onClick={() => router.push('/register')}
                                        className="w-full py-3 bg-white/10 hover:bg-white/20 rounded-xl font-semibold transition"
                                    >
                                        Commencer gratuitement
                                    </button>
                                ) : (
                                    <button
                                        onClick={() => handleSubscribe(tier.id)}
                                        disabled={loading === tier.id}
                                        className={`w-full py-3 bg-gradient-to-r ${tier.color} hover:opacity-90 rounded-xl font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed`}
                                    >
                                        {loading === tier.id ? 'Chargement...' : 'S\'abonner'}
                                    </button>
                                )}
                            </div>
                        )
                    })}
                </div>

                {/* FAQ or Additional Info */}
                <div className="mt-16 text-center">
                    <p className="text-gray-500 text-sm">
                        Paiement sécurisé via Stripe • Annulation possible à tout moment
                    </p>
                </div>
            </div>
        </div>
    )
}
