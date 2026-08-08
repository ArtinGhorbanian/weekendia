"""Small process-local abuse and load guards.

These controls are intentionally modest. They are thread-safe within one Python
process, but they are not shared across workers or hosts and must not be
presented as a replacement for an edge or distributed rate limiter.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable


class SlidingWindowRateLimiter:
    """Thread-safe, in-memory, per-key sliding-window rate limiter."""

    def __init__(
        self,
        limit: int,
        window_seconds: float,
        clock: Callable[[], float] = time.monotonic,
        max_keys: int = 10_000,
    ) -> None:
        if limit < 1 or window_seconds <= 0 or max_keys < 1:
            raise ValueError("Rate limiter bounds must be positive.")
        self.limit = limit
        self.window_seconds = window_seconds
        self._clock = clock
        self._max_keys = max_keys
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._overflow_events: deque[float] = deque()
        self._lock = threading.Lock()

    def check(self, key: str) -> tuple[bool, int, int]:
        """Consume one request and return allowed, remaining, retry-after."""

        now = self._clock()
        cutoff = now - self.window_seconds
        with self._lock:
            if key in self._events:
                events = self._events[key]
            else:
                if len(self._events) >= self._max_keys:
                    self._prune_empty_keys(cutoff)
                if len(self._events) < self._max_keys:
                    events = self._events[key]
                else:
                    # Bound attacker-controlled key cardinality. New keys share
                    # one conservative overflow bucket until old keys expire.
                    events = self._overflow_events
            while events and events[0] <= cutoff:
                events.popleft()

            if len(events) >= self.limit:
                retry_after = max(1, int(events[0] + self.window_seconds - now + 0.999))
                return False, 0, retry_after

            events.append(now)
            remaining = self.limit - len(events)
            return True, remaining, 0

    def _prune_empty_keys(self, cutoff: float) -> None:
        for candidate in list(self._events):
            events = self._events[candidate]
            while events and events[0] <= cutoff:
                events.popleft()
            if not events:
                del self._events[candidate]


class ConcurrencyGuard:
    """Non-blocking process-local guard for expensive plan generations."""

    def __init__(self, limit: int) -> None:
        if limit < 1:
            raise ValueError("Concurrency limit must be positive.")
        self.limit = limit
        self._semaphore = threading.BoundedSemaphore(limit)

    def try_acquire(self) -> bool:
        return self._semaphore.acquire(blocking=False)

    def release(self) -> None:
        self._semaphore.release()


__all__ = ["ConcurrencyGuard", "SlidingWindowRateLimiter"]
