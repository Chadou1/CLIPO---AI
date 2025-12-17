'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { authApi } from '@/lib/api'
import { toast } from 'sonner'
import Link from 'next/link'

export default function ForgotPasswordPage() {
    const router = useRouter()
    const [step, setStep] = useState<'email' | 'code' | 'password'>('email')
    const [email, setEmail] = useState('')
    const [code, setCode] = useState('')
    const [newPassword, setNewPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [loading, setLoading] = useState(false)

    const handleRequestCode = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)

        try {
            await authApi.post('/auth/forgot-password', { email })
            toast.success('Reset code sent to your email!')
            setStep('code')
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to send code')
        } finally {
            setLoading(false)
        }
    }

    const handleVerifyCode = (e: React.FormEvent) => {
        e.preventDefault()

        if (code.length !== 8) {
            toast.error('Please enter the 8-digit code')
            return
        }

        setStep('password')
    }

    const handleResetPassword = async (e: React.FormEvent) => {
        e.preventDefault()

        if (newPassword !== confirmPassword) {
            toast.error('Passwords do not match')
            return
        }

        if (newPassword.length < 6) {
            toast.error('Password must be at least 6 characters')
            return
        }

        setLoading(true)

        try {
            await authApi.post('/auth/reset-password', {
                email,
                code,
                new_password: newPassword
            })

            toast.success('Password reset successfully!')
            router.push('/login')
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Password reset failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center p-4">
            <div className="max-w-md w-full bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">🔐 Reset Password</h1>
                    <p className="text-gray-300">
                        {step === 'email' && 'Enter your email to receive a reset code'}
                        {step === 'code' && 'Enter the 8-digit code sent to your email'}
                        {step === 'password' && 'Choose a new password'}
                    </p>
                </div>

                {/* Step 1: Email */}
                {step === 'email' && (
                    <form onSubmit={handleRequestCode} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-200 mb-2">
                                Email Address
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="your@email.com"
                                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Sending...' : 'Send Reset Code'}
                        </button>
                    </form>
                )}

                {/* Step 2: Code */}
                {step === 'code' && (
                    <form onSubmit={handleVerifyCode} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-200 mb-2">
                                Reset Code
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
                            disabled={code.length !== 8}
                            className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Verify Code
                        </button>

                        <button
                            type="button"
                            onClick={() => setStep('email')}
                            className="w-full py-2 text-gray-400 hover:text-white transition text-sm"
                        >
                            ← Use different email
                        </button>
                    </form>
                )}

                {/* Step 3: New Password */}
                {step === 'password' && (
                    <form onSubmit={handleResetPassword} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-200 mb-2">
                                New Password
                            </label>
                            <input
                                type="password"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                                placeholder="••••••••"
                                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-200 mb-2">
                                Confirm Password
                            </label>
                            <input
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                placeholder="••••••••"
                                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Resetting...' : 'Reset Password'}
                        </button>
                    </form>
                )}

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
