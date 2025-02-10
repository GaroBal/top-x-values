import cProfile
import functools
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

PROFILE_DIR = Path("profiles")
PROFILE_DIR.mkdir(exist_ok=True)


def get_run_dir():
    """Create and return a timestamped directory for this profiling run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = PROFILE_DIR / timestamp
    run_dir.mkdir(exist_ok=True)
    return run_dir


@contextmanager
def profile_context(filename: str):
    """Context manager for profiling code blocks."""
    # Get/create the run directory on first profile of a request
    if not hasattr(profile_context, "current_run_dir"):
        profile_context.current_run_dir = get_run_dir()

    profiler = cProfile.Profile()
    profiler.enable()
    try:
        yield profiler
    finally:
        profiler.disable()
        # Save stats to the run directory
        stats_path = profile_context.current_run_dir / f"{filename}.stats"
        profiler.dump_stats(str(stats_path))


def profile_function(func):
    """Decorator for profiling individual functions."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with profile_context(func.__name__):
            return func(*args, **kwargs)

    return wrapper
