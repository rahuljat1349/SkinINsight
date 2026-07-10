"""Simple in-memory rate limiter"""

import time
from collections import defaultdict
from typing import Dict, List, Tuple


class RateLimiter:
    """Sliding-window rate limiter per client IP."""

    def __init__(self, max_requests: int = 1, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: Dict[str, List[float]] = defaultdict(list)

    def check(self, client_ip: str) -> Tuple[bool, int]:
        """
        Returns (allowed, retry_after_seconds).
        If allowed is False, the request should be rejected.
        """
        now = time.time()
        cutoff = now - self.window_seconds

        bucket = self._buckets[client_ip]
        # Prune expired timestamps
        bucket[:] = [t for t in bucket if t > cutoff]

        if len(bucket) >= self.max_requests:
            oldest = bucket[0]
            retry_after = int(self.window_seconds - (now - oldest))
            return False, max(retry_after, 1)

        bucket.append(now)
        return True, 0

    def get_remaining(self, client_ip: str) -> int:
        now = time.time()
        cutoff = now - self.window_seconds
        bucket = self._buckets.get(client_ip, [])
        active = sum(1 for t in bucket if t > cutoff)
        return max(0, self.max_requests - active)
