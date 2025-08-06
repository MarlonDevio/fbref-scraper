from typing import AsyncIterator, Tuple
import re
from scrapy import Spider
from scrapy.http import Request, Response
from typing import Any
from ..items import ClubItem


class ClubSpider(Spider):
    name = "club_spider"

    async def start(self) -> AsyncIterator[Any]:
        urls = [
            "https://www.fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats",
        ]

        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response: Response, **kwargs) -> Any:
        teams_xpath = '//table[contains(@id, "overall")]//td[contains(@class,"left") and contains(@data-stat, "team")]/a/@href'
        urls = response.xpath(teams_xpath)
        for url in urls:
            id, name = self._extract_club_id_and_club_name(url.get())
            club_item = ClubItem()
            club_item['club_id'] = id
            club_item['club_name'] = name
            print("EXTRACTED URLS. ID: ", id, ", NAME: ", name)
            yield club_item

    def _extract_club_id_and_club_name(self, club_url: str) -> Tuple[str, str] | None:
        pattern = r"\/en\/squads\/(\w+)\/\w+-\w+\/(.+)-Stats"
        match = re.match(pattern, club_url)
        if not match:
            return None
        club_id = match.group(1).strip()
        club_name = match.group(2).replace("-"," ").strip()
        return club_id, club_name
