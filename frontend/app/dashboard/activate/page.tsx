'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Key, Sparkles } from 'lucide-react'
import api from '@/lib/api'
import { toast } from 'sonner'

export default function ActivatePage() {
    const router = useRouter()
    const [loading, setLoading] = useState(false)
    const [code, setCode] = useState('')

    const handleActivate = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)

        try {
            const response = await api.post('/auth/activate', {
                activation_code: code.toUpperCase()
            })

            toast.success(response.data.message)
            router.push('/dashboard')
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Activation failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-950 via-purple-950 to-gray-950 flex items-center justify-center p-6">
            <div className="w-full max-w-md">
                <Link href="/dashboard" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition mb-6">
                    ← Retour au dashboard
                </Link>

                {/* Activation Card */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full mb-4">
                            <Key className="w-8 h-8 text-white" />
                        </div>
                        <h1 className="text-3xl font-bold text-white mb-2">Activer PRO</h1>
                        <p className="text-gray-400">Entrez votre code d'activation pour débloquer PRO</p>
                    </div>

                    <form onSubmit={handleActivate} className="space-y-6">
                        {/* Activation Code */}
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Code d'Activation
                            </label>
                            <input
                                type="text"
                                required
                                value={code}
                                onChange={(e) => setCode(e.target.value.toUpperCase())}
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white text-center text-lg font-mono placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                                placeholder="XXXX-XXXX-XXXX"
                                maxLength={16}
                            />
                        </div>

                        {/* Benefits */}
                        <div className="p-4 bg-purple-600/10 rounded-lg border border-purple-500/30">
                            <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
                                <Sparkles className="w-5 h-5 text-purple-400" />
                                Avantages PRO
                            </h3>
                            <ul className="space-y-1 text-sm text-gray-300">
                                <li>✅ 100 crédits offerts</li>
                                <li>✅ Accès pendant 30 jours</li>
                                <li>✅ Clips sans watermark</li>
                                <li>✅ Export HD 1080p</li>
                                <li>✅ Traitement prioritaire</li>
                            </ul>
                        </div>

                        {/* Submit */}
                        <button
                            type="submit"
                            disabled={loading || code.length < 12}
                            className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Activation...' : 'Activer mon compte'}
                        </button>
                    </form>

                    {/* Available Codes Info */}
                    <div className="mt-6 p-4 bg-blue-600/10 rounded-lg border border-blue-500/30">
                        <p className="text-sm text-blue-300 text-center">
                            💡 <strong>Codes de test disponibles:</strong><br />
                            Consultez le fichier <code className="bg-black/30 px-2 py-1 rounded">activation_codes.json</code> dans le backend
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}
