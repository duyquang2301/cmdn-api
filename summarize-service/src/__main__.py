"""Package entry point."""

from .tasks.worker import start_worker

if __name__ == "__main__":
    start_worker()
