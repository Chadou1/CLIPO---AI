/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['s3.amazonaws.com'], // Add your S3 bucket domain
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:32190',
  },
  async rewrites() {
    return [
      {
        source: '/api/videos',
        destination: 'http://localhost:32191/videos',
      },
      {
        source: '/api/videos/:path*',
        destination: 'http://localhost:32191/videos/:path*',
      },
      {
        source: '/api/clips/:path*',
        destination: 'http://localhost:32191/clips/:path*',
      },
      {
        source: '/api/processing/:path*',
        destination: 'http://localhost:32191/processing/:path*',
      },
      {
        source: '/api/uploads/:path*',
        destination: 'http://localhost:32191/uploads/:path*',
      },
      {
        source: '/api/:path*',
        destination: 'http://localhost:32190/:path*',
      },
    ]
  },
}

module.exports = nextConfig
