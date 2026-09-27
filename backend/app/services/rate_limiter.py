import os
import time
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    """
    In-memory sliding window rate limiter for endpoint protection.
    Suitable for single-instance or containerized deployments.
    Can be complemented with AWS WAF / CloudFront rate limiting at the infrastructure edge.
    """

    def __init__(self, requests_limit: int = 15, window_seconds: int = 60):
        self.limit = requests_limit
        self.window = window_seconds
        self.records: Dict[str, List[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client and request.client.host:
            return request.client.host
        return "127.0.0.1"

    def check(self, request: Request, key_suffix: str = "") -> None:
        # Allow disabling during automated test runs
        if os.environ.get("DISABLE_RATE_LIMITER", "false").lower() == "true":
            return
        if os.environ.get("TESTING", "false").lower() == "true":
            return

        ip = self._get_client_ip(request)
        key = f"{ip}:{key_suffix}" if key_suffix else ip
        now = time.time()
        cutoff = now - self.window

        # Filter out timestamps older than the sliding window
        valid_timestamps = [ts for ts in self.records[key] if ts > cutoff]
        self.records[key] = valid_timestamps

        if len(valid_timestamps) >= self.limit:
            oldest = valid_timestamps[0]
            retry_after = max(1, int(self.window - (now - oldest)))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many attempts. Please try again after {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )

        self.records[key].append(now)

    def reset(self) -> None:
        self.records.clear()


# Shared instances
auth_rate_limiter = SlidingWindowRateLimiter(requests_limit=20, window_seconds=60)
google_rate_limiter = SlidingWindowRateLimiter(requests_limit=30, window_seconds=60)
