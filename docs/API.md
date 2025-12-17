# API Documentation

## Base URL

```
Production: https://api.clipgenius.ai
Development: http://localhost:8000
```

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "credits": 3,
  "plan": "free"
}
```

#### POST /auth/login
Login to existing account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### POST /auth/refresh
Refresh access token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Videos

#### POST /videos/upload
Upload a video for processing.

**Headers:**
```
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**Form Data:**
- `file`: Video file (MP4, MOV, AVI, MKV - max 500MB)

**Response:**
```json
{
  "id": 123,
  "filename": "myvideo.mp4",
  "status": "uploaded",
  "created_at": "2024-01-01T00:00:00",
  "clips_count": 0
}
```

#### GET /videos/
Get all videos for authenticated user.

**Response:**
```json
[
  {
    "id": 123,
    "filename": "myvideo.mp4",
    "duration": 300.5,
    "status": "finished",
    "created_at": "2024-01-01T00:00:00",
    "clips_count": 5
  }
]
```

#### GET /videos/{id}
Get specific video details.

**Response:**
```json
{
  "id": 123,
  "filename": "myvideo.mp4",
  "duration": 300.5,
  "status": "finished",
  "created_at": "2024-01-01T00:00:00",
  "clips_count": 5
}
```

#### GET /videos/{id}/clips
Get all clips for a video.

**Response:**
```json
[
  {
    "id": 1,
    "start_time": 15.5,
    "end_time": 45.2,
    "viral_score": 85.5,
    "style": "simple",
    "transcript_segment": "This is the hook...",
    "created_at": "2024-01-01T00:05:00",
    "download_url": "https://..."
  }
]
```

### Processing

#### POST /process/start
Start video processing.

**Request Body:**
```json
{
  "video_id": 123
}
```

**Response:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "Processing started"
}
```

#### GET /process/status/{task_id}
Check processing status.

**Response:**
```json
{
  "state": "PROCESSING",
  "status": "Generating clip 2/5...",
  "result": {
    "progress": 40
  }
}
```

### Clips

#### POST /clips/{id}/export
Export a clip (costs 1 credit).

**Request Body:**
```json
{
  "style": "simple"
}
```

**Response:**
```json
{
  "download_url": "https://s3.amazonaws.com/...",
  "credits_remaining": 29
}
```

#### DELETE /clips/{id}
Delete a clip.

**Response:**
```
204 No Content
```

### Billing

#### GET /billing/info
Get billing information for authenticated user.

**Response:**
```json
{
  "plan": "pro",
  "credits": 85,
  "stripe_customer_id": "cus_123",
  "next_renewal": "2024-02-01T00:00:00"
}
```

#### POST /billing/create-checkout-session
Create Stripe checkout session for subscription.

**Request Body:**
```json
{
  "plan": "pro"
}
```

**Response:**
```json
{
  "checkout_url": "https://checkout.stripe.com/..."
}
```

#### POST /billing/webhook
Stripe webhook endpoint (used by Stripe, not clients).

## Error Responses

All endpoints may return the following error formats:

**400 Bad Request:**
```json
{
  "detail": "Invalid request data"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Could not validate credentials"
}
```

**402 Payment Required:**
```json
{
  "detail": "Insufficient credits"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

- Free plan: 10 requests/minute
- Starter plan: 30 requests/minute
- Pro plan: 100 requests/minute
- Agency plan: Unlimited

## Webhooks

### Video Processing Complete

When video processing completes, you can configure a webhook URL to receive notifications.

**Payload:**
```json
{
  "event": "video.processing.complete",
  "video_id": 123,
  "clips_count": 5,
  "timestamp": "2024-01-01T00:10:00"
}
```
