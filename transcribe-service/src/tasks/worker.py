"""Celery worker entry point."""

import multiprocessing
import sys

from loguru import logger

from src.config import settings

from . import transcription_tasks  # noqa: F401
from .celery_app import app


def start_worker():
    """Start Celery worker with configured options."""
    try:
        multiprocessing.set_start_method("spawn", force=True)
    except RuntimeError:
        pass

    logger.info("🚀 Starting Transcribe Worker")
    logger.info("Configuration:")
    logger.info(f"  - Broker: {settings.get_rabbitmq_url()}")
    logger.info(f"  - Backend: {settings.redis_url}")
    logger.info("  - Queue: audio.transcribe")
    logger.info(f"  - Autoscale: {settings.celery_autoscale}")
    logger.info(f"  - Prefetch: {settings.celery_prefetch_multiplier}")
    logger.info(f"  - Max tasks per child: {settings.celery_max_tasks_per_child}")
    logger.info(f"  - Log level: {settings.log_level}")

    autoscale_parts = settings.celery_autoscale.split(",")
    autoscale_arg = (
        f"{autoscale_parts[0]},{autoscale_parts[1]}"
        if len(autoscale_parts) == 2
        else "10,1"
    )
    if autoscale_arg == "10,1":
        logger.warning(
            f"Invalid autoscale format: {settings.celery_autoscale}, using default: {autoscale_arg}"
        )

    worker_args = [
        "worker",
        "--pool",
        "solo",
        "--loglevel",
        settings.log_level.lower(),
        "--queues",
        "audio.transcribe",
        "--autoscale",
        autoscale_arg,
        "--max-tasks-per-child",
        str(settings.celery_max_tasks_per_child),
    ]
    worker_args.extend(sys.argv[1:])

    logger.info(f"Starting worker with args: {' '.join(worker_args)}")

    try:
        app.worker_main(worker_args)
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.exception(f"Worker failed: {e}")
        raise


if __name__ == "__main__":
    start_worker()
