from typing import AsyncIterator, Tuple
import re
from scrapy import Spider
from scrapy.http import Request, Response
from typing import Any
from fbref_scraper.fbref_scraper.items import ClubItem


class ClubSpider(Spider):
    name = "club_spider"

    async def start(self) -> AsyncIterator[Any]:
        urls = ["https://www.fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats", ]

        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        teams_xpath = '//table[contains(@id, "overall")]//td[contains(@class,"left") and contains(@data-stat, "team")]/a/@href'

    def _extract_club_id(self, club_url: str) -> str:
        pattern = r"/en"
