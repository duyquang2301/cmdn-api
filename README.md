# Audio Transcription & Summarization Platform

## Quick Start (Local)

### 1. Prerequisites

```bash
# Install Python 3.12+
python --version

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install FFmpeg (for audio processing)
brew install ffmpeg  # macOS
```

### 2. Setup Infrastructure

```bash
# Start PostgreSQL, Redis, RabbitMQ, MinIO
docker compose up -d postgres redis rabbitmq minio
```

### 3. Configure Environment

```bash
# Copy environment file
cp .env.example .env

### 4. Install Dependencies
make install

### 5. Run Migrations
make migrate

### 6. Start Services

Open 3 terminals and run:

# Terminal 1: API Gateway
make api

# Terminal 2: Transcribe Service
make transcribe

# Terminal 3: Summarize Service
make summarize
```

### 7. Test

```bash
# API Documentation
open http://localhost:8000/docs

# Upload audio
curl -X POST "http://localhost:8000/api/v1/meetings/upload" \
  -F "file=@meeting.mp3" \
  -F "title=Test Meeting"
```

## Quick Start (Docker)

```bash
# 1. Setup
cp .env.example .env
# Edit .env with your LLM_API_KEY

# 2. Start all services
make up

# 3. Run migrations
make migrate

# 4. Access
open http://localhost:8000/docs
```

## Development Commands

```bash
make format       # Format code
make lint         # Check code quality
make clean        # Clean cache
make logs         # View logs (Docker)
make restart      # Restart services (Docker)
```
