'use client'

import Link from 'next/link'
import { XCircle, ArrowLeft, RefreshCw } from 'lucide-react'

export default function PaymentCancelPage() {
    return (
        <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center p-4">
            <div className="max-w-md w-full bg-white/5 backdrop-blur-sm border border-red-500/30 rounded-2xl p-8 text-center">
                <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                    <XCircle className="w-10 h-10 text-red-400" />
                </div>

                <h1 className="text-3xl font-bold text-white mb-4">Paiement annulé</h1>
                <p className="text-gray-400 mb-8">
                    Votre paiement a été annulé et aucun frais n'a été prélevé.
                </p>

                <div className="space-y-3">
                    <Link
                        href="/pricing"
                        className="flex items-center justify-center gap-2 w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg font-semibold transition"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Réessayer
                    </Link>

                    <Link
                        href="/dashboard"
                        className="flex items-center justify-center gap-2 w-full py-3 bg-white/10 hover:bg-white/20 rounded-lg font-semibold transition"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Retour au Dashboard
                    </Link>
                </div>

                <p className="text-xs text-gray-500 mt-6">
                    Des questions? Contactez notre support à support@clipo.ai
                </p>
            </div>
        </div>
    )
}
