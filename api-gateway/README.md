# Meeting Management API

FastAPI application for meeting management with audio transcription.

## Quick Start

```bash
# Install dependencies
uv sync

# Setup secrets
cp config/local/.secrets.toml.example config/local/.secrets.toml
# Edit config/local/.secrets.toml with your credentials

# Start database
make db-up

# Run migrations
make migrate

# Run server
make run
```

Server runs at `http://localhost:8000`

## Configuration

Secrets are stored in `config/local/.secrets.toml` (not committed to git):
- PostgreSQL credentials
- AWS S3 credentials
- Auth0 credentials

For local development, you can disable authentication in `config/local/config.toml`:
```toml
[auth0]
ENABLED = false
```

## Authentication

All `/api/v1/*` endpoints require Auth0 JWT authentication.

See `docs/AUTH0_SETUP.md` for complete setup guide.

## API Endpoints

### Public
- `GET /health/` - Health check

### Protected (requires JWT)
- `POST /api/v1/meetings/` - Create meeting
- `GET /api/v1/meetings/` - List meetings
- `GET /api/v1/meetings/{id}/` - Get meeting
- `PUT /api/v1/meetings/{id}/` - Update meeting
- `DELETE /api/v1/meetings/{id}/` - Delete meeting
- `POST /api/v1/meetings/upload` - Upload audio

### Making Authenticated Requests

```bash
curl -X POST http://localhost:8000/api/v1/meetings/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Meeting"}'
```

## Development

```bash
make dev          # Run with auto-reload
make format       # Format code
make lint         # Run linters
make test         # Run tests
```

## Tech Stack

- FastAPI + Dishka
- PostgreSQL + SQLAlchemy + Alembic
- S3 + Celery
- Auth0 JWT Authentication
- Python 3.12+

## Documentation

- `docs/AUTH_SETUP.md` - Auth0 setup and configuration
- `docs/ARCHITECTURE_PATTERNS.md` - Architecture patterns explained
