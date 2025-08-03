from typing import Any, Generator

import scrapy
from scrapy.http import Response, TextResponse

from ..items import ClubItem
from ..utils.urls import extract_club_id, extract_club_name


class ClubUrlsSpider(scrapy.Spider):
    name = "club_urls"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # URLs for the top 5 leagues' current season stats pages
        self.start_urls = [
            "https://fbref.com/en/comps/9/Premier-League-Stats",      # Premier League
            # "https://fbref.com/en/comps/12/La-Liga-Stats",            # La Liga
            # "https://fbref.com/en/comps/13/Ligue-1-Stats",            # Ligue 1
            # "https://fbref.com/en/comps/20/Bundesliga-Stats",         # Bundesliga
            # "https://fbref.com/en/comps/11/Serie-A-Stats",            # Serie A
        ]
    
    def parse(self, response: Response, **kwargs):
        """
        Parse competition stats page to extract club URLs.
        
        Args:
            response: HTTP response object containing the competition stats page
            
        Yields:
            scrapy.Request: Requests to individual club pages
        """
        if not isinstance(response, TextResponse):
            return
        
        # Extract league/competition name from URL
        league_name = self._extract_league_name(response.url)
        
        # Extract club URLs using xpath from doc.md
        # //table[contains(@id, "overall")]//td[contains(@class, "left") and contains(@data-stat, "team")]//a
        club_links = response.xpath(
            '//table[contains(@id, "overall")]//td[contains(@class, "left") and contains(@data-stat, "team")]//a/@href'
        ).getall()
        print("CLUB LINKS", club_links)
        for link in club_links:
            print(extract_club_name(link))

            if link:
                club_url = response.urljoin(link)
                yield self.parse_club(club_url)
                # yield scrapy.Request(
                #     url=club_url,
                #     callback=self.parse_club,
                #     meta={
                #         'club_url': club_url,
                #         'league': league_name,
                #         'season': self._extract_season_from_url(club_url),
                #         'name': extract_club_name(link)
                #     }
                # )
    
    def parse_club(self, url: str):
        """
        Parse individual club page to extract club information.
        
        Args:
            url: HTTP response object containing the club page
            
        Yields:
            ClubItem: Club item with detailed information
        """

        club_url = url # response.meta.get('club_url', response.url)
        league = self._extract_league_name(url) #response.meta.get('league', 'Unknown')
        season = "Unknown"
        club_name = extract_club_name(club_url)

        club_item = ClubItem()
        club_item['club_id'] = extract_club_id(club_url)
        club_item['url'] = club_url
        club_item['league'] = league
        club_item['season'] = season
        club_item['name'] = club_name
        club_item['country'] = "unknown"
        club_item['players_count'] = 0


        # Extract club name from page title or header

        # Extract country information
        # country = response.xpath('//p[contains(text(), "Country:")]//following-sibling::text()').get()
        # if not country:
        #     # Alternative xpath for country
        #     country = response.xpath('//span[contains(@class, "f-i")]/@title').get()
        # if country:
        #     club_item['country'] = country.strip()
        
        # Count players in the squad
        # player_links = response.xpath(
        #     '//table[contains(@id, "standard")]//th[contains(@class, "left") and contains(@data-stat, "player")]//a'
        # )
        # club_item['players_count'] = len(player_links)
        
        return club_item
    
    def _extract_league_name(self, url: str) -> str:
        """Extract league name from the competition URL."""
        if "Premier-League" in url:
            return "Premier League"
        elif "La-Liga" in url:
            return "La Liga"
        elif "Ligue-1" in url:
            return "Ligue 1"
        elif "Bundesliga" in url:
            return "Bundesliga"
        elif "Serie-A" in url:
            return "Serie A"
        else:
            return "Unknown"
    
    def _extract_season_from_url(self, url: str) -> str:
        """Extract season from club URL."""
        import re
        match = re.search(r'/(\d{4}-\d{4})/', url)
        return match.group(1) if match else "Unknown"
