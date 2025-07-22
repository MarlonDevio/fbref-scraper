from pydantic_settings import BaseSettings
from typing import List, Dict, Any


class Settings(BaseSettings):
    # Downloader settings
    REQUEST_TIMEOUT: int = 15
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    RETRY_ATTEMPTS: int = 3
    RETRY_BACKOFF_FACTOR: float = 0.5
    CONCURRENT_REQUESTS: int = 4
    REQUESTS_PER_MINUTE: int = 8


settings = Settings()
