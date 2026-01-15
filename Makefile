SERVICES := api-gateway transcribe-service summarize-service

.PHONY: help install clean api transcribe summarize up down logs migrate build restart format format-check lint lint-fix test

help:
	@echo "Development:"
	@echo "  make install  - Install dependencies"
	@echo "  make clean    - Clean cache"
	@echo "  make api      - Run API Gateway"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format   - Format code"
	@echo "  make lint     - Lint code"
	@echo "  make lint-fix - Fix linting issues"
	@echo "  make test     - Run tests"
	@echo ""
	@echo "Docker:"
	@echo "  make up       - Start services"
	@echo "  make down     - Stop services"
	@echo "  make logs     - View logs"

install:
	@cd api-gateway && uv sync --group dev
	@cd transcribe-service && uv sync --extra dev
	@cd summarize-service && uv sync --group dev

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

api:
	@cd api-gateway/src && uv run python -m app.run

transcribe:
	@cd transcribe-service && uv run -m src

summarize:
	@cd summarize-service && uv run -m src

format:
	@for s in $(SERVICES); do cd $$s && uv run ruff format src && cd ..; done

format-check:
	@for s in $(SERVICES); do cd $$s && uv run ruff format --check src && cd ..; done

lint:
	@for s in $(SERVICES); do cd $$s && uv run ruff check src || true && cd ..; done

lint-fix:
	@for s in $(SERVICES); do cd $$s && uv run ruff check --fix src && cd ..; done

test:
	@cd api-gateway && uv run pytest tests/ || true
	@cd transcribe-service && uv run pytest tests/ || true
	@cd summarize-service && uv run pytest tests/ || true

build:
	@docker-compose build

up:
	@docker-compose up -d

down:
	@docker-compose down

restart:
	@docker-compose restart

logs:
	@docker-compose logs -f

migrate:
	@cd api-gateway && PYTHONPATH=src uv run alembic upgrade head
