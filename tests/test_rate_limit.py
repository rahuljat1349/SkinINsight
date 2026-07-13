"""Rate limiter unit tests"""

import time
from app.core.ratelimit import RateLimiter


class TestRateLimiter:
    def test_allows_first_request(self):
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        allowed, retry_after = limiter.check("127.0.0.1")
        assert allowed is True
        assert retry_after == 0

    def test_blocks_second_request(self):
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        limiter.check("127.0.0.1")
        allowed, retry_after = limiter.check("127.0.0.1")
        assert allowed is False
        assert retry_after > 0

    def test_allows_different_ips(self):
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        limiter.check("192.168.1.1")
        allowed, _ = limiter.check("192.168.1.2")
        assert allowed is True

    def test_allows_multiple_requests(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        for _ in range(3):
            allowed, _ = limiter.check("10.0.0.1")
            assert allowed is True
        allowed, _ = limiter.check("10.0.0.1")
        assert allowed is False

    def test_window_expiry(self):
        limiter = RateLimiter(max_requests=1, window_seconds=1)
        limiter.check("127.0.0.1")
        time.sleep(1.1)
        allowed, _ = limiter.check("127.0.0.1")
        assert allowed is True

    def test_get_remaining(self):
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        assert limiter.get_remaining("10.0.0.1") == 5
        limiter.check("10.0.0.1")
        assert limiter.get_remaining("10.0.0.1") == 4

    def test_retry_after_value(self):
        limiter = RateLimiter(max_requests=1, window_seconds=10)
        limiter.check("10.0.0.1")
        _, retry_after = limiter.check("10.0.0.1")
        assert 1 <= retry_after <= 10

    def test_multiple_ips_independent(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        limiter.check("A")
        limiter.check("A")
        assert limiter.get_remaining("A") == 0
        assert limiter.get_remaining("B") == 2
