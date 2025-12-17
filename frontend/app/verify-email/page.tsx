'use client'

import { useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { authApi } from '@/lib/api'
import { toast } from 'sonner'
import Link from 'next/link'

export default function VerifyEmailPage() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const email = searchParams.get('email') || ''

    const [code, setCode] = useState('')
    const [loading, setLoading] = useState(false)
    const [resending, setResending] = useState(false)

    const handleVerify = async (e: React.FormEvent) => {
        e.preventDefault()

        if (code.length !== 8) {
            toast.error('Please enter the 8-digit code')
            return
        }

        setLoading(true)

        try {
            await authApi.post('/auth/verify-email', {
                email,
                code
            })

            toast.success('Email verified successfully!')
            router.push('/login')
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Verification failed')
        } finally {
            setLoading(false)
        }
    }

    const handleResend = async () => {
        setResending(true)

        try {
            await authApi.post('/auth/resend-verification', {
                email
            })

            toast.success('Verification code sent!')
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to resend code')
        } finally {
            setResending(false)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center p-4">
            <div className="max-w-md w-full bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">📧 Verify Your Email</h1>
                    <p className="text-gray-300">
                        We've sent an 8-digit code to<br />
                        <span className="font-semibold text-purple-400">{email}</span>
                    </p>
                </div>

                <form onSubmit={handleVerify} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-200 mb-2">
                            Verification Code
                        </label>
                        <input
                            type="text"
                            value={code}
                            onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 8))}
                            placeholder="12345678"
                            maxLength={8}
                            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 text-center text-2xl font-bold tracking-widest"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading || code.length !== 8}
                        className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Verifying...' : 'Verify Email'}
                    </button>
                </form>

                <div className="mt-6 text-center">
                    <p className="text-gray-400 text-sm mb-2">
                        Didn't receive the code?
                    </p>
                    <button
                        onClick={handleResend}
                        disabled={resending}
                        className="text-purple-400 hover:text-purple-300 font-semibold text-sm transition disabled:opacity-50"
                    >
                        {resending ? 'Sending...' : 'Resend Code'}
                    </button>
                </div>

                <div className="mt-8 text-center">
                    <Link
                        href="/login"
                        className="text-gray-400 hover:text-white text-sm transition"
                    >
                        ← Back to Login
                    </Link>
                </div>
            </div>
        </div>
    )
}
