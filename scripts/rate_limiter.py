"""
Rate limiter utilities for external APIs.

Implements rate limiting for arXiv and Semantic Scholar APIs to respect
their usage policies and avoid getting blocked.
"""
import time
import logging
from typing import Callable, Any
from functools import wraps
from collections import deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter implementation.

    This ensures we don't exceed API rate limits by tracking
    request timestamps and enforcing delays.
    """

    def __init__(self, max_requests: int, time_window: int, min_delay: float = 0):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
            min_delay: Minimum delay between requests in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.min_delay = min_delay
        self.requests = deque()
        self.last_request_time = None

    def _clean_old_requests(self):
        """Remove requests outside the current time window."""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)

        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()

    def wait_if_needed(self):
        """
        Wait if necessary to respect rate limits.

        This method:
        1. Removes old requests from tracking
        2. Waits if we've hit the max requests in the time window
        3. Enforces minimum delay between requests
        """
        now = datetime.now()

        # Clean up old requests
        self._clean_old_requests()

        # Check if we need to wait for the time window
        if len(self.requests) >= self.max_requests:
            oldest = self.requests[0]
            wait_until = oldest + timedelta(seconds=self.time_window)
            wait_time = (wait_until - now).total_seconds()

            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self._clean_old_requests()

        # Enforce minimum delay between requests
        if self.last_request_time and self.min_delay > 0:
            elapsed = (now - self.last_request_time).total_seconds()
            if elapsed < self.min_delay:
                delay = self.min_delay - elapsed
                logger.debug(f"Enforcing minimum delay: {delay:.2f}s")
                time.sleep(delay)

        # Record this request
        self.requests.append(datetime.now())
        self.last_request_time = datetime.now()

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator to rate limit a function.

        Usage:
            @rate_limiter
            def my_api_call():
                ...
        """
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            self.wait_if_needed()
            return func(*args, **kwargs)
        return wrapper


# Pre-configured rate limiters for common APIs

# arXiv API Rate Limiter
# arXiv requests a 3-second delay between requests
# No official rate limit, but they can block aggressive scrapers
arxiv_rate_limiter = RateLimiter(
    max_requests=20,      # Conservative limit
    time_window=60,       # Per minute
    min_delay=3.0         # 3 seconds between requests (arXiv recommendation)
)

# Semantic Scholar API Rate Limiter
# Free tier: 100 requests per 5 minutes (300 seconds)
# With API key: 5,000 requests per 5 minutes
semantic_scholar_rate_limiter = RateLimiter(
    max_requests=100,     # Free tier limit
    time_window=300,      # 5 minutes
    min_delay=3.0         # 3 seconds between requests to be safe
)

# Rate limiter for Semantic Scholar with API key
# Use this if you have an API key
semantic_scholar_api_key_limiter = RateLimiter(
    max_requests=5000,    # With API key
    time_window=300,      # 5 minutes
    min_delay=0.1         # Minimal delay with API key
)


def with_retry(max_retries: int = 3, backoff: float = 2.0):
    """
    Decorator to retry a function with exponential backoff.

    Useful for handling transient API errors or rate limit responses.

    Args:
        max_retries: Maximum number of retry attempts
        backoff: Backoff multiplier (exponential)

    Usage:
        @with_retry(max_retries=3, backoff=2.0)
        def my_api_call():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt < max_retries:
                        wait_time = backoff ** attempt
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {str(e)}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")

            raise last_exception

        return wrapper
    return decorator


# Example usage functions

@arxiv_rate_limiter
@with_retry(max_retries=3, backoff=2.0)
def fetch_from_arxiv(url: str) -> Any:
    """
    Fetch data from arXiv API with rate limiting and retry logic.

    This is a template function - implement your actual arXiv API call here.
    """
    import requests
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response


@semantic_scholar_rate_limiter
@with_retry(max_retries=3, backoff=2.0)
def fetch_from_semantic_scholar(paper_id: str, api_key: str = None) -> Any:
    """
    Fetch data from Semantic Scholar API with rate limiting and retry logic.

    Args:
        paper_id: Paper identifier
        api_key: Optional API key for higher rate limits

    This is a template function - implement your actual Semantic Scholar API call here.
    """
    import requests

    url = f"https://api.semanticscholar.org/v1/paper/{paper_id}"
    headers = {}

    if api_key:
        headers['x-api-key'] = api_key

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()
