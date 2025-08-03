import scrapy
from scrapy.http import Response, TextResponse
from fbref_scraper.items import SeasonItem
from fbref_scraper.utils.urls import extract_season_id


class SeasonSpider(scrapy.Spider):
    name = "seasons"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Start with history pages for major competitions
        self.start_urls = [
            "https://fbref.com/en/comps/9/history/Premier-League-Seasons",
            "https://fbref.com/en/comps/12/history/La-Liga-Seasons", 
            "https://fbref.com/en/comps/13/history/Ligue-1-Seasons",
            "https://fbref.com/en/comps/20/history/Bundesliga-Seasons",
            "https://fbref.com/en/comps/11/history/Serie-A-Seasons",
        ]
    
    def parse(self, response: Response, **kwargs):
        """
        Parse competition history page to extract season URLs.
        
        Args:
            response: HTTP response object containing the competition history page
            
        Yields:
            scrapy.Request: Requests to individual season pages
        """
        if not isinstance(response, TextResponse):
            return
            
        # Extract competition info
        competition_name = self._extract_competition_name(response.url)
        competition_url = response.url
        
        # Extract season URLs using xpath pattern from existing spider
        # Look for season links in the seasons table
        season_links = response.xpath('//table[@id="seasons"]//th[@data-stat="year_id"]//a')
        
        for season_link in season_links:
            season_text = season_link.xpath('.//text()').get()
            season_url = season_link.xpath('.//@href').get()
            
            if season_text and season_url:
                # Only process seasons from 2010 onwards (adjust as needed)
                if self._is_valid_season(season_text):
                    full_season_url = response.urljoin(season_url)
                    yield scrapy.Request(
                        url=full_season_url,
                        callback=self.parse_season,
                        meta={
                            'season_year': season_text.strip(),
                            'competition_name': competition_name,
                            'competition_url': competition_url,
                            'season_url': full_season_url
                        }
                    )
    
    def parse_season(self, response: Response):
        """
        Parse individual season page to extract season information and clubs.
        
        Args:
            response: HTTP response object containing the season page
            
        Yields:
            SeasonItem: Season item with detailed information
        """
        if not isinstance(response, TextResponse):
            return
            
        season_year = response.meta.get('season_year', 'Unknown')
        competition_name = response.meta.get('competition_name', 'Unknown')
        competition_url = response.meta.get('competition_url', '')
        season_url = response.meta.get('season_url', response.url)
        
        season_item = SeasonItem()
        season_item['season_id'] = extract_season_id(season_url)
        season_item['year'] = season_year
        season_item['competition'] = competition_name
        season_item['competition_url'] = competition_url
        season_item['url'] = season_url
        
        # Extract clubs participating in this season
        clubs = []
        club_links = response.xpath(
            '//table[contains(@id, "overall") or contains(@id, "results")]//td[contains(@class, "left") and contains(@data-stat, "team")]//a'
        )
        
        for club_link in club_links:
            club_name = club_link.xpath('.//text()').get()
            club_url = club_link.xpath('.//@href').get()
            
            if club_name and club_url:
                clubs.append({
                    'name': club_name.strip(),
                    'url': response.urljoin(club_url)
                })
        
        season_item['clubs'] = clubs
        
        yield season_item
    
    def _extract_competition_name(self, url: str) -> str:
        """Extract competition name from history URL."""
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
    
    def _is_valid_season(self, season_text: str) -> bool:
        """Check if season is valid/recent enough to process."""
        import re
        # Extract year from season text (e.g., "2023-2024" -> 2023)
        match = re.search(r'(\d{4})', season_text)
        if match:
            year = int(match.group(1))
            return year >= 2010  # Only process seasons from 2010 onwards
        return False
