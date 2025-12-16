<<<<<<< HEAD
# Clipo

**AI-Powered TikTok/Reels Clip Generator**

Transform your long-form videos into viral short clips automatically using AI.

## Features

- 🎬 **AI Viral Detection** - Automatically finds the best moments in your videos
- ✂️ **Auto Clip Generation** - Cuts clips at optimal timestamps
- 📝 **Animated Subtitles** - TikTok-style captions with emojis
- 🎯 **Auto Reframing** - Smart 9:16 vertical format with face tracking
- 📊 **Viral Score** - Each clip gets a score based on engagement potential
- 💳 **Credit System** - Flexible pricing with subscription plans

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Celery + Redis** - Async task queue
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **FFmpeg** - Video processing
- **MoviePy** - Video  editing
- **Whisper / Faster-Whisper** - AI transcription
- **DeepFace** - Face detection
- **OpenAI GPT** - Viral scoring and content analysis
- **Stripe** - Payment processing
- **AWS S3** - Video storage

### Frontend
- **Next.js 14** - React framework with App Router
- **TailwindCSS** - Styling
- **React Query** - Data fetching
- **Zustand** - State management
- **Axios** - HTTP client
- **React Player** - Video playback

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OR:
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 15+
  - Redis
  - FFmpeg

### Using Docker (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/clipo.git
cd clipo
```

2. **Set up environment variables**
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Frontend
cp frontend/.env.local.example frontend/.env.local
```

3. **Start all services**
```bash
docker-compose -f infrastructure/docker-compose.yml up --build
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Flower (Celery Monitor): http://localhost:5555

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
python -c "from models import init_db; init_db()"

# Start backend server
uvicorn main:app --reload --port 8000

# In another terminal, start Celery worker
celery -A workers.celery_config worker --loglevel=info
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.local.example .env.local

# Start development server
npm run dev
```

## Configuration

### Backend Environment Variables

See `backend/.env.example` for all available options:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key
- `AWS_ACCESS_KEY_ID` - AWS credentials for S3
- `STRIPE_SECRET_KEY` - Stripe API key
- `OPENAI_API_KEY` - OpenAI API key for GPT
- `RESEND_API_KEY` - Email service API key

### Frontend Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

**Authentication**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `POST /auth/refresh` - Refresh token

**Videos**
- `POST /videos/upload` - Upload video
- `GET /videos/` - List user videos
- `GET /videos/{id}` - Get video details
- `GET /videos/{id}/clips` - Get video clips

**Processing**
- `POST /process/start` - Start processing
- `GET /process/status/{task_id}` - Check status

**Clips**
- `POST /clips/{id}/export` - Export clip (costs 1 credit)
- `DELETE /clips/{id}` - Delete clip

**Billing**
- `GET /billing/info` - Get billing info
- `POST /billing/create-checkout-session` - Start subscription
- `POST /billing/webhook` - Stripe webhook

## Video Processing Pipeline

1. **Upload** - Video uploaded to S3
2. **Extract Audio** - FFmpeg extracts audio track
3. **Transcription** - Whisper generates transcript with timestamps
4. **Scene Detection** - Identifies scene changes
5. **Face Detection** - Tracks faces for auto-reframing
6. **Viral Analysis** - GPT scores segments for viral potential
7. **Clip Generation** - Creates clips at optimal timestamps
8. **Effects** - Adds subtitles, reframes to 9:16, applies zoom
9. **Export** - Renders final MP4 clips

## Pricing Plans

- **Free**: 3 clips/month
- **Starter**: €10/month - 30 clips
- **Pro**: €20/month - 100 clips
- **Agency**: €49/month - 500 clips

## Deployment

### Docker Deployment

The project includes production-ready Docker configuration:

```bash
docker-compose -f infrastructure/docker-compose.yml up -d
```

### Cloud Deployment

**AWS EC2**
1. Launch Ubuntu instance with GPU (for faster processing)
2. Install Docker & Docker Compose
3. Clone repo and configure environment
4. Run docker-compose

**Render / Railway**
1. Connect GitHub repo
2. Configure environment variables
3. Deploy backend and frontend separately

## Development

### Running Tests

**Backend**
```bash
cd backend
pytest
```

**Frontend**
```bash
cd frontend
npm test
```

### Code Structure

```
clipo/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── models/              # Database models
│   ├── api/                 # API endpoints
│   ├── workers/             # Celery tasks
│   ├── video/               # Video processing
│   ├── utils/               # Utilities
│   └── billing/             # Stripe integration
├── frontend/
│   ├── app/                 # Next.js pages
│   ├── components/          # React components
│   ├── lib/                 # Utilities
│   └── hooks/               # Custom hooks
└── infrastructure/
    ├── docker-compose.yml   # Docker setup
    ├── Dockerfile.backend   # Backend image
    ├── Dockerfile.frontend  # Frontend image
    └── nginx.conf           # Reverse proxy
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [github.com/yourusername/clipo/issues]
- Email: support@clipo.ai

## Acknowledgments

- OpenAI Whisper for transcription
- FFmpeg for video processing
- Stripe for payments
- Next.js & FastAPI teams
=======
# CLIPO---AI
>>>>>>> 8a4fd783adf7b3f53d54e0bb80047466a485013a
