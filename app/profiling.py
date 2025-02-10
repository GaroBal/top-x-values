import cProfile
import functools
import time
from pathlib import Path
from contextlib import contextmanager

PROFILE_DIR = Path("profiles")
PROFILE_DIR.mkdir(exist_ok=True)

@contextmanager
def profile_context(filename: str):
    """Context manager for profiling code blocks."""
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        yield profiler
    finally:
        profiler.disable()
        # Save stats to profiles directory with timestamp
        stats_path = PROFILE_DIR / f"{filename}_{int(time.time())}.stats"
        profiler.dump_stats(str(stats_path))

def profile_function(func):
    """Decorator for profiling individual functions."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        with profile_context(func.__name__):
            return await func(*args, **kwargs)
    return wrapper