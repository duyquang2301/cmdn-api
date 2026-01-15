FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install minimal build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    libavformat-dev \
    libavcodec-dev \
    libavutil-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project

COPY . ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

FROM python:3.12-slim-bookworm AS final

ARG APP_UID=10001
ARG APP_GID=10001

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g ${APP_GID} appgroup && \
    useradd -u ${APP_UID} -g ${APP_GID} -s /usr/sbin/nologin appuser && \
    mkdir -p /home/appuser && chown -R ${APP_UID}:${APP_GID} /home/appuser

WORKDIR /app

ENV VIRTUAL_ENV="/app/.venv" \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME="/home/appuser/.cache/huggingface" \
    HOME="/home/appuser"

COPY --from=builder --chown=${APP_UID}:${APP_GID} /app/ ./

# Create uploads directory
RUN mkdir -p /app/uploads && chown -R ${APP_UID}:${APP_GID} /app/uploads

USER appuser

CMD ["python", "-m", "src"]
