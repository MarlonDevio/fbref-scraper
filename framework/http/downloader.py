import asyncio
import time
from httpx_curl_cffi import AsyncCurlTransport
from httpx import Limits, Timeout, AsyncClient

from tenacity import retry, stop_after_attempt, wait_fixed, RetryError

from .request import Request
from .response import Response
from framework.settings import settings

import logging

logger = logging.getLogger(__name__)


class TokenBucket:
    """
    A token bucket for rate limiting.
    """

    def __init__(self, requests_per_minute: int):
        self.rate = 60.0 / requests_per_minute
        self.last_request_time = 0

    async def acquire(self):
        """
        Wait until a token is available.
        """
        now = time.monotonic()
        logger.info(f"now monotonic: {now}")
        logger.info(f"Last request time: {self.last_request_time}")
        time_since_last = now - self.last_request_time
        logger.info(f"Time since last: {time_since_last}")

        if time_since_last < self.rate:
            logger.info("Sleeping")
            await asyncio.sleep(self.rate - time_since_last)

        self.last_request_time = time.monotonic()


class Downloader:
    def __init__(self):
        self._client = AsyncClient(
            transport=AsyncCurlTransport(
                impersonate="chrome",
                default_headers=True,
            ),
            headers=settings.DEFAULT_HEADERS,
            timeout=Timeout(settings.REQUEST_TIMEOUT),
            limits=Limits(max_connections=settings.CONCURRENT_REQUESTS),
            follow_redirects=True,
        )
        self.rate_limiter = TokenBucket(settings.REQUESTS_PER_MINUTE)

    @retry(
        stop=stop_after_attempt(settings.RETRY_ATTEMPTS),
        wait=wait_fixed(settings.RETRY_BACKOFF_FACTOR),
    )
    async def fetch(self, request: Request) -> Response | None:
        await self.rate_limiter.acquire()
        logger.info(f"Downloading: {request.url}")

        try:
            http_response = await self._client.get(request.url)
            http_response.raise_for_status()
            return Response(
                url=str(http_response.url),
                status_code=http_response.status_code,
                content=http_response.content,
                request=request,
            )
        except RetryError as e:
            logger.exception(f"Max retries exceeded for {request.url}: {e}")
            return None
        except Exception as e:
            logger.exception(f"Failed to download {request.url}: {e}")
            return None

    async def close(self) -> None:
        await self._client.aclose()
