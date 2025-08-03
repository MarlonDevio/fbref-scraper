import scrapy
from scrapy.http import Response, TextResponse
from fbref_scraper.items import PlayerItem
from fbref_scraper.utils.urls import extract_player_id, extract_club_id


class PlayerUrlsSpider(scrapy.Spider):
    name = "player_urls"
    
    custom_settings = {
        'DOWNLOAD_DELAY': 10,  # Increased delay for player pages
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    }
    
    def __init__(self, club_urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Can be initialized with specific club URLs, or use default top clubs
        if club_urls:
            self.start_urls = club_urls.split(',')
        else:
            # Default to some major club URLs for testing
            self.start_urls = [
                "https://fbref.com/en/squads/b8fd03ef/2024-2025/Manchester-City-Stats",
                "https://fbref.com/en/squads/18bb7c10/2024-2025/Arsenal-Stats",
                "https://fbref.com/en/squads/cff3d9bb/2024-2025/Chelsea-Stats",
                "https://fbref.com/en/squads/19538871/2024-2025/Manchester-United-Stats",
                "https://fbref.com/en/squads/822bd0ba/2024-2025/Liverpool-Stats",
            ]
    
    def parse(self, response: Response, **kwargs):
        """
        Parse club page to extract player URLs.
        
        Args:
            response: HTTP response object containing the club page
            
        Yields:
            scrapy.Request: Requests to individual player pages
        """
        if not isinstance(response, TextResponse):
            return
        
        # Extract club info for context
        club_name = self._extract_club_name(response)
        club_id = extract_club_id(response.url)
        season = self._extract_season_from_url(response.url)
        league = self._extract_league_from_url(response.url)
        
        # Extract player URLs using xpath from doc.md
        # //table[contains(@id, "standard")]//th[contains(@class, "left") and contains(@data-stat, "player")]//a
        player_links = response.xpath(
            '//table[contains(@id, "standard")]//th[contains(@class, "left") and contains(@data-stat, "player")]//a/@href'
        ).getall()
        
        for link in player_links:
            if link:
                player_url = response.urljoin(link)
                yield scrapy.Request(
                    url=player_url,
                    callback=self.parse_player,
                    meta={
                        'player_url': player_url,
                        'club_name': club_name,
                        'club_id': club_id,
                        'season': season,
                        'league': league
                    }
                )
    
    def parse_player(self, response: Response):
        """
        Parse individual player page to extract player information.
        
        Args:
            response: HTTP response object containing the player page
            
        Yields:
            PlayerItem: Player item with detailed information
        """
        if not isinstance(response, TextResponse):
            return
        
        player_url = response.meta.get('player_url', response.url)
        club_name = response.meta.get('club_name', 'Unknown')
        
        player_item = PlayerItem()
        player_item['player_id'] = extract_player_id(player_url)
        player_item['url'] = player_url
        player_item['club'] = club_name
        
        # Extract player name from page title or header
        full_name = response.xpath('//h1/span/text()').get()
        if full_name:
            name_parts = full_name.strip().split()
            if len(name_parts) >= 2:
                player_item['first_name'] = ' '.join(name_parts[:-1])
                player_item['last_name'] = name_parts[-1]
            else:
                player_item['first_name'] = full_name
                player_item['last_name'] = ''
        
        # Extract date of birth
        dob = response.xpath('//span[contains(text(), "Born:")]/following-sibling::text()').get()
        if not dob:
            dob = response.xpath('//p[contains(text(), "Born:")]/text()').re_first(r'Born:\s*([\d-]+)')
        if dob:
            player_item['date_of_birth'] = dob.strip()
        
        # Extract position
        position = response.xpath('//p[contains(text(), "Position:")]/text()').re_first(r'Position:\s*([^,]+)')
        if not position:
            position = response.xpath('//span[contains(text(), "Position:")]/following-sibling::text()').get()
        if position:
            player_item['position'] = position.strip()
        
        # Extract nationality
        nationality = response.xpath('//span[contains(@class, "f-i")]/@title').get()
        if not nationality:
            nationality = response.xpath('//p[contains(text(), "Citizenship:")]/text()').re_first(r'Citizenship:\s*([^,]+)')
        if nationality:
            player_item['nationality'] = nationality.strip()
        
        yield player_item
    
    def _extract_club_name(self, response: Response) -> str:
        """Extract club name from the page."""
        if not isinstance(response, TextResponse):
            return "Unknown"
        
        # Try to get club name from page title or header
        club_name = response.xpath('//h1/text()').get()
        if club_name:
            # Clean the name (remove season info if present)
            return club_name.split('20')[0].strip() if '20' in club_name else club_name.strip()
        return "Unknown"
    
    def _extract_season_from_url(self, url: str) -> str:
        """Extract season from URL."""
        import re
        match = re.search(r'/(\d{4}-\d{4})/', url)
        return match.group(1) if match else "Unknown"
    
    def _extract_league_from_url(self, url: str) -> str:
        """Extract league from URL context."""
        # This would need to be enhanced based on the squad URL structure
        # For now, return Unknown as we'd need additional context
        return "Unknown"
