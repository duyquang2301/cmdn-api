"""Celery application configuration."""

from celery import Celery

from src.config import settings

app = Celery("transcribe", broker=settings.get_rabbitmq_url(), backend=settings.redis_url)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_default_queue="audio.transcribe",
    task_routes={
        "audio.transcribe.start": {"queue": "audio.transcribe"},
        "audio.transcribe.chunk": {"queue": "audio.transcribe"},
        "audio.transcribe.merge": {"queue": "audio.transcribe"},
    },
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,
    result_backend_transport_options={"master_name": "mymaster"},
    worker_prefetch_multiplier=settings.celery_prefetch_multiplier,
    worker_max_tasks_per_child=settings.celery_max_tasks_per_child,
    timezone="UTC",
    enable_utc=True,
)
