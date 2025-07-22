from abc import ABC, abstractmethod
from typing import Any, List


class BaseParser(ABC):
    def __init__(self, content: str) -> None:
        self._document = self._load_document(content)

    @abstractmethod
    def _load_document(self, content: str) -> Any:
        """
        Loads content into the parser's internal document representation.
        """
        pass

    @abstractmethod
    def css(self, selector: str) -> List[Any]:
        """
        Select elements using a CSS selector.
        """
        pass

    @abstractmethod
    def xpath(self, query: str) -> List[Any]:
        """
        Select elements using an XPath query
        """
        pass
