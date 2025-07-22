from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from functools import cached_property
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .request import Request
    from framework.parsers.base_parser import BaseParser


@dataclass
class Response:
    url: str
    status_code: int
    content: bytes
    request: "Request"
    parser: Optional["BaseParser"] = None

    @cached_property
    def text(self) -> str:
        logger.info("Decoding content")
        return self.content.decode("utf-8", errors="replace")
