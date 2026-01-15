"""Package entry point for running as module.

This module allows the src package to be run as a module using:
    python -m src

It imports and calls the start_worker function from the worker module.
"""

from .tasks.worker import start_worker

if __name__ == "__main__":
    start_worker()
