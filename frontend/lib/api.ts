import axios from 'axios'

const AUTH_API_URL = '/api'
const VIDEO_API_URL = '/api'

// Auth Service API
export const authApi = axios.create({
    baseURL: AUTH_API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Video Service API
export const videoApi = axios.create({
    baseURL: VIDEO_API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Helper to attach interceptors to an instance
const attachInterceptors = (instance: any) => {
    // Request interceptor for adding auth token
    instance.interceptors.request.use(
        (config: any) => {
            const token = localStorage.getItem('access_token')
            if (token) {
                config.headers.Authorization = `Bearer ${token}`
            }
            return config
        },
        (error: any) => {
            return Promise.reject(error)
        }
    )

    // Response interceptor for handling token refresh
    instance.interceptors.response.use(
        (response: any) => response,
        async (error: any) => {
            const originalRequest = error.config

            if (error.response?.status === 401 && !originalRequest._retry) {
                originalRequest._retry = true

                try {
                    const refreshToken = localStorage.getItem('refresh_token')
                    if (refreshToken) {
                        // Refresh token always goes to Auth Service
                        const response = await axios.post(`${AUTH_API_URL}/auth/refresh`, {
                            refresh_token: refreshToken,
                        })

                        const { access_token, refresh_token } = response.data
                        localStorage.setItem('access_token', access_token)
                        localStorage.setItem('refresh_token', refresh_token)

                        originalRequest.headers.Authorization = `Bearer ${access_token}`
                        return instance(originalRequest)
                    }
                } catch (err) {
                    // Refresh failed, logout user
                    localStorage.removeItem('access_token')
                    localStorage.removeItem('refresh_token')
                    window.location.href = '/login'
                }
            }

            return Promise.reject(error)
        }
    )
}

attachInterceptors(authApi)
attachInterceptors(videoApi)

// Default export is authApi for backward compatibility
export default authApi
