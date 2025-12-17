#!/bin/bash

# ClipGenius AI - Quick Start Script

echo "🚀 Starting ClipGenius AI..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment files if they don't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env from example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your API keys before continuing."
    read -p "Press enter to continue after editing backend/.env..."
fi

if [ ! -f frontend/.env.local ]; then
    echo "📝 Creating frontend/.env.local from example..."
    cp frontend/.env.local.example frontend/.env.local
fi

# Start services
echo "🐳 Starting Docker containers..."
docker-compose -f infrastructure/docker-compose.yml up --build -d

echo "✅ Services started successfully!"
echo ""
echo "📍 Access points:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Celery Flower: http://localhost:5555"
echo ""
echo "📖 View logs:"
echo "   docker-compose -f infrastructure/docker-compose.yml logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose -f infrastructure/docker-compose.yml down"
