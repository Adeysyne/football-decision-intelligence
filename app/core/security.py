import threading
import time
from collections import defaultdict, deque


class InMemoryRateLimiter:
    """
    Small single-process rate limiter for the private beta.

    This protects the current pilot deployment from accidental
    flooding and basic brute-force attempts.

    A shared gateway/Redis-backed limiter should replace this
    before horizontally scaled production deployment.
    """

    def __init__(self) -> None:
        self._events: dict[
            str,
            deque[float],
        ] = defaultdict(
            deque
        )

        self._lock = (
            threading.Lock()
        )

    def allow(
        self,
        *,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> bool:
        if limit <= 0:
            return False

        now = time.monotonic()

        cutoff = (
            now
            - window_seconds
        )

        with self._lock:
            bucket = (
                self._events[
                    key
                ]
            )

            while (
                bucket
                and bucket[0]
                <= cutoff
            ):
                bucket.popleft()

            if len(
                bucket
            ) >= limit:
                return False

            bucket.append(
                now
            )

            return True

    def retry_after(
        self,
        *,
        key: str,
        window_seconds: int,
    ) -> int:
        now = time.monotonic()

        with self._lock:
            bucket = (
                self._events.get(
                    key
                )
            )

            if not bucket:
                return 1

            remaining = (
                window_seconds
                - (
                    now
                    - bucket[0]
                )
            )

        return max(
            1,
            int(
                remaining
            )
            + 1,
        )

    def clear(
        self,
    ) -> None:
        with self._lock:
            self._events.clear()


security_limiter = (
    InMemoryRateLimiter()
)