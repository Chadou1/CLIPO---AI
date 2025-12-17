# ClipGenius AI - Production Deployment Guide

## AWS EC2 Deployment

### 1. Launch EC2 Instance

```bash
# Recommended instance: t3.xlarge or g4dn.xlarge (with GPU)
# OS: Ubuntu 22.04 LTS
# Storage: At least 50GB
```

### 2. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install NVIDIA Docker (for GPU instances)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### 3. Deploy Application

```bash
# Clone repository
git clone https://github.com/yourusername/clipgenius.git
cd clipgenius

# Set up environment
cp backend/.env.example backend/.env
# Edit backend/.env with production values

# Start services
docker-compose -f infrastructure/docker-compose.yml up -d

# Check logs
docker-compose -f infrastructure/docker-compose.yml logs -f
```

### 4. Configure Domain & SSL

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Render Deployment

### Backend

1. Create new Web Service
2. Connect GitHub repository
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

### Frontend

1. Create new Static Site
2. Connect GitHub repository
3. Set build command: `cd frontend && npm install && npm run build`
4. Set publish directory: `frontend/.next`
5. Deploy

## Railway Deployment

1. Create new project
2. Add PostgreSQL database
3. Add Redis database
4. Deploy backend from GitHub
5. Deploy frontend from GitHub
6. Configure environment variables

## Environment Variables Checklist

**Critical for Production:**
- [ ] `SECRET_KEY` - Use strong random key
- [ ] `DATABASE_URL` - Production database
- [ ] `REDIS_URL` - Production Redis
- [ ] `AWS_ACCESS_KEY_ID` - AWS credentials
- [ ] `AWS_SECRET_ACCESS_KEY` - AWS secret
- [ ] `S3_BUCKET_NAME` - Production bucket
- [ ] `STRIPE_SECRET_KEY` - Live Stripe key
- [ ] `STRIPE_WEBHOOK_SECRET` - Stripe webhook
- [ ] `OPENAI_API_KEY` - OpenAI API key
- [ ] `RESEND_API_KEY` - Email service
- [ ] `FRONTEND_URL` - Production frontend URL
- [ ] `BACKEND_URL` - Production backend URL

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Backup database regularly
- [ ] Monitor logs for suspicious activity

## Performance Optimization

- [ ] Enable Redis caching
- [ ] Use CDN for video files
- [ ] Configure database connection pooling
- [ ] Enable gzip compression
- [ ] Optimize video encoding settings
- [ ] Scale Celery workers based on load
- [ ] Monitor resource usage

## Monitoring

- [ ] Set up application monitoring (Sentry)
- [ ] Configure log aggregation
- [ ] Set up uptime monitoring
- [ ] Monitor database performance
- [ ] Track API response times
- [ ] Monitor Celery queue length

## Backup Strategy

```bash
# Database backup
docker exec clipgenius_postgres pg_dump -U clipgenius clipgenius > backup.sql

# Restore
docker exec -i clipgenius_postgres psql -U clipgenius clipgenius < backup.sql
```

## Scaling

### Horizontal Scaling

- Run multiple Celery workers
- Use load balancer for API
- Separate database server
- Use managed Redis service

### Vertical Scaling

- Upgrade instance type
- Increase worker concurrency
- Optimize video processing settings

## Maintenance

```bash
# Update application
git pull
docker-compose -f infrastructure/docker-compose.yml up --build -d

# View logs
docker-compose -f infrastructure/docker-compose.yml logs -f

# Restart service
docker-compose -f infrastructure/docker-compose.yml restart backend

# Clean up
docker system prune -a
```
