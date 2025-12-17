import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
    id: number
    email: string
    credits: number
    plan: string
}

interface AuthState {
    user: User | null
    accessToken: string | null
    refreshToken: string | null
    isAuthenticated: boolean
    setUser: (user: User) => void
    setTokens: (accessToken: string, refreshToken: string) => void
    logout: () => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            setUser: (user) => set({ user, isAuthenticated: true }),
            setTokens: (accessToken, refreshToken) => {
                localStorage.setItem('access_token', accessToken)
                localStorage.setItem('refresh_token', refreshToken)
                set({ accessToken, refreshToken })
            },
            logout: () => {
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false })
            },
        }),
        {
            name: 'auth-storage',
        }
    )
)
