from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Type


class BasePipelineStep(ABC):
    @abstractmethod
    async def process_item(
        self, item: BaseModel, scraper: Type["BaseScraper"]
    ) -> BaseModel:
        """
        Process an item. Must return the item for the next stage.
        Can raise DropItem exception to halt processing for this item.
        """
        pass
