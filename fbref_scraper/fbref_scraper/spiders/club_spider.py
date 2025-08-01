from collections.abc import AsyncIterator
from typing import Any, List, Callable
from scrapy.http import Response, TextResponse

import scrapy
from scrapy.link import Link
from scrapy.linkextractors import LinkExtractor


class ClubSpider(scrapy.Spider):
    name = "clubs"
    link_extractor = LinkExtractor(
        restrict_xpaths='//table[contains(@id,"season")]//th[@data-stat="year_id"]',
        restrict_text="20[1-9]+-20[0-9]+$",
    )

    async def start(self) -> AsyncIterator[Any]:
        urls = [
            "https://fbref.com/en/comps/9/history/Premier-League-Seasons",
            "https://fbref.com/en/comps/12/history/La-Liga-Seasons",
            "https://fbref.com/en/comps/13/history/Ligue-1-Seasons",
            "https://fbref.com/en/comps/20/history/Bundesliga-Seasons",
            "https://fbref.com/en/comps/11/history/Serie-A-Seasons",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response) -> Any | None:
        """
        Parses the given HTTP response to extract and return a JSON object containing URLs.

        Args:
            response (Response): The HTTP response object to parse.

        Returns:
            dict or None: A dictionary with a heading (derived from the response URL) as the key and a list of extracted URLs as the value, or None if the response is not a TextResponse.
        """
        urls: List[Link] = []
        heading = self._create_name(response.url, lambda x: x.split("/")[-1])

        if not isinstance(response, TextResponse):
            return None

        urls: List[Link] = self.link_extractor.extract_links(response)

        json_obj = {heading: [url.url for url in urls]}
        return json_obj

    def _create_name(self, name: str, callback: Callable[[str], str]|None = None) -> str:
        if callback is None:
            return name
        return callback(name)


