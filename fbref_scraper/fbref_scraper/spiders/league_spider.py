from typing import AsyncIterator, Tuple
import re
from scrapy import Spider
from scrapy.http import Request, Response
from typing import Any


class LeagueSpider(Spider):
    name = "league_spider"

    async def start(self) -> AsyncIterator[Any]:
        urls = [
            "https://www.fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats",
            "https://www.fbref.com/en/comps/12/2024-2025/2024-2025-La-Liga-Stats",
            "https://www.fbref.com/en/comps/11/2024-2025/2024-2025-Serie-A-Stats",
            "https://www.fbref.com/en/comps/20/2024-2025/2024-2025-Bundesliga-Stats",
            "https://www.fbref.com/en/comps/13/2024-2025/2024-2025-Ligue-1-Stats",
        ]
        for url in urls:
            league_id, season, league = self._extract_season_and_league(url)
            yield Request(url=url, callback=self.parse,
                          meta={"league_id": league_id, "league": league, "season": season})

    def parse(self, response: Response, **kwargs) -> Any:

        league_id = response.meta.get("league_id", "unknown")
        league = response.meta.get("league", "unknown")
        season = response.meta.get("season", "unknown")

        print("LEAGUE ID = ", league_id)
        print("LEAGUEEEEEEEEE = ", league)
        print("SEASONNNNNNNN = ", season)

    def _extract_season_and_league(self, url_to_parse: str) -> Tuple[str, str, str]:
        pattern = r"https:\/\/w{3}.fbref.com\/en\/comps\/(\d+)\/\d{4}-\d{4}\/(\d{4}-\d{4}).([A-Za-z\-\d?]+)-Stats"
        match = re.search(pattern, url_to_parse)
        if not match:
            return "unknown", "unknown", "unknown"
        return match.group(1), match.group(2), match.group(3)
