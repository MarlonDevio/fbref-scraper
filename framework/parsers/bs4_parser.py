from bs4 import BeautifulSoup, Tag, _RawAttributeValue
from typing import Any, List
from .base_parser import BaseParser


class ElementWrapper:
    """
    Wrapper around a BeautifulSoup Tag to provide a consistent Api.
    """

    def __init__(self, element: Tag):
        self._element = element

    def text(self, strip: bool = True) -> str:
        return self._element.get_text(strip=strip)

    def css(self, selector: str) -> List["ElementWrapper"]:
        return [ElementWrapper(e) for e in self._element.select(selector)]


class BS4Parser(BaseParser):
    def __init__(self, content: str) -> None:
        super().__init__(content)

    def _load_document(self, content: str) -> Any:
        # Parse HTML content into a BeautifulSoup document
        return BeautifulSoup(content, "lxml")

    def css(self, selector: str) -> List[ElementWrapper]:
        # Select elements using CSS selector and wrap them
        return [ElementWrapper(el) for el in self._document.select(selector)]

    def xpath(self, query: str) -> List[ElementWrapper]:
        # BeautifulSoup does not support XPath
        raise NotImplementedError("XPath is not supported by BS4Parser")
