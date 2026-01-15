# Summarize Service

Meeting summarization service using Google Gemini AI with Clean Architecture.

## Features

- 📝 AI-powered meeting summarization
- 🔑 Key notes extraction
- ✅ **Automatic task generation from transcript**
- 📦 Chunk-based processing for large transcripts
- 🔄 Autoscaling workers (min=1, max=10)
- 🏗️ Clean Architecture (Domain, Application, Infrastructure, Presentation)
- 🐳 Docker support
- 📊 Status tracking with detailed error handling

## Architecture

```
src/
├── domain/              # Business logic
│   ├── entities/       # Meeting (Aggregate Root)
│   ├── enums/          # MeetingStatus
│   └── ports/          # Interfaces
├── application/        # Use cases
│   └── use_cases/      # SummarizeTranscript
├── infrastructure/     # External services
│   ├── config/         # Settings, logging, prompts
│   ├── persistence/    # Database
│   ├── repositories/   # Implementations
│   └── services/       # Gemini AI
└── presentation/       # Entry points
    ├── celery/         # Celery tasks
    └── di/             # Dependency Injection
```

## Quick Start

### Local Development

```bash
# Install dependencies
make sync

# Run worker
make run
```

### Docker

```bash
# Build and run
make docker-build
make docker-up

# View logs
make docker-logs

# Restart
make docker-restart

# Rebuild from scratch
make docker-rebuild
```

## Configuration

Create `.env` file in `summarize-service/`:

```bash
# Database (shared with api-gateway)
DATABASE_URL=postgresql://audio_user:audio_pass@localhost:5432/audio_db

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASS=admin123

# Redis
REDIS_URL=redis://localhost:6379/0

# Google Gemini
GOOGLE_API_KEY=your_api_key_here
LLM_MODEL=gemini-2.0-flash-exp

# Summarization
SUMMARY_CHUNK_SIZE=1000000

# Worker
CELERY_AUTOSCALE=10,1
```

## Status Flow

```
transcribed → summarizing → summarized → completed
                  ↓
          summarize_failed
```

See [STATUS_FLOW.md](../docs/STATUS_FLOW.md) for details.

## Tasks

- `summarize_transcript_task` - Generate summary, extract key notes, and create tasks from transcript

## Features

### Summary Generation
- Automatic chunking for large transcripts
- Vietnamese language support
- Professional meeting minutes format
- Markdown output

### Key Notes Extraction
- Decision tracking
- Action items with assignees and deadlines
- Risk identification
- Priority classification

### Task Generation
- Automatic extraction of action items from transcript
- Direct database access (Clean Architecture)
- Includes title, description, assignee, and due date
- Transaction safety with batch insert
- Graceful error handling (won't fail summarization if task creation fails)

## Development

```bash
# Run locally
uv run -m src

# Clean cache
make clean

# Sync dependencies
make sync
```

## Prompts

Prompts are configured in `src/infrastructure/config/prompts.py`:
- `CHUNK_SUMMARY_PROMPT` - Summarize individual chunks
- `FINAL_SUMMARY_PROMPT` - Merge summaries into final format
- `KEY_NOTES_PROMPT` - Extract key notes with JSON format
- `GENERATE_TASKS_PROMPT` - Generate actionable tasks from transcript
