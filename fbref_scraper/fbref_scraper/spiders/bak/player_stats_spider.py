import scrapy
from scrapy.http import Response, TextResponse
from fbref_scraper.items import PlayerStatsItem
from fbref_scraper.utils.urls import extract_player_id, extract_club_id


class PlayerStatsSpider(scrapy.Spider):
    name = "player_stats"
    
    custom_settings = {
        'DOWNLOAD_DELAY': 12,  # Increased delay for stats pages
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    }
    
    def __init__(self, player_urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Can be initialized with specific player URLs
        if player_urls:
            self.start_urls = player_urls.split(',')
        else:
            # Default empty - should be populated by other spiders or passed as argument
            self.start_urls = []
    
    def parse(self, response: Response, **kwargs):
        """
        Parse player page to extract detailed statistics.
        
        Args:
            response: HTTP response object containing the player page
            
        Yields:
            PlayerStatsItem: Player statistics item
        """
        if not isinstance(response, TextResponse):
            return
        
        player_id = extract_player_id(response.url)
        
        # Extract player stats from the stats table
        # Look for the main stats table (usually has ID like "stats_standard")
        stats_rows = response.xpath('//table[contains(@id, "stats")]//tbody//tr')
        
        for row in stats_rows:
            # Skip header rows or summary rows
            if row.xpath('.//th').get():
                continue
                
            # Extract season info
            season = row.xpath('.//th[@data-stat="season"]//a/text()').get()
            if not season:
                season = row.xpath('.//th[@data-stat="season"]/text()').get()
            
            # Skip if no season (likely a total row)
            if not season or season.strip() in ['Career', 'Total', '']:
                continue
            
            # Extract club info
            club_cell = row.xpath('.//td[@data-stat="team"]')
            club_name = club_cell.xpath('.//a/text()').get()
            club_url = club_cell.xpath('.//a/@href').get()
            
            # Extract league info
            league = row.xpath('.//td[@data-stat="comp_level"]//a/text()').get()
            if not league:
                league = row.xpath('.//td[@data-stat="comp_level"]/text()').get()
            
            # Extract position
            position = row.xpath('.//td[@data-stat="position"]/text()').get()
            
            # Extract statistical data
            matches_played = self._extract_stat(row, 'matches')
            if not matches_played:
                matches_played = self._extract_stat(row, 'games')
            
            goals = self._extract_stat(row, 'goals')
            assists = self._extract_stat(row, 'assists')
            yellow_cards = self._extract_stat(row, 'cards_yellow')
            red_cards = self._extract_stat(row, 'cards_red')
            minutes_played = self._extract_stat(row, 'minutes')
            
            # Create stats item
            stats_item = PlayerStatsItem()
            stats_item['player_id'] = player_id
            stats_item['season'] = season.strip() if season else 'Unknown'
            stats_item['club'] = club_name.strip() if club_name else 'Unknown'
            stats_item['league'] = league.strip() if league else 'Unknown'
            stats_item['position'] = position.strip() if position else 'Unknown'
            stats_item['matches_played'] = self._to_int(matches_played)
            stats_item['goals'] = self._to_int(goals)
            stats_item['assists'] = self._to_int(assists)
            stats_item['yellow_cards'] = self._to_int(yellow_cards)
            stats_item['red_cards'] = self._to_int(red_cards)
            stats_item['minutes_played'] = self._to_int(minutes_played)
            stats_item['url'] = response.url
            
            yield stats_item
    
    def _extract_stat(self, row, stat_name: str) -> str:
        """Extract a specific statistic from a table row."""
        stat_value = row.xpath(f'.//td[@data-stat="{stat_name}"]/text()').get()
        return stat_value.strip() if stat_value else '0'
    
    def _to_int(self, value: str) -> int:
        """Convert string value to integer, handling various formats."""
        if not value or value == '':
            return 0
        
        # Remove any non-numeric characters except decimals
        import re
        cleaned = re.sub(r'[^\d.]', '', str(value))
        
        try:
            # Convert to float first to handle decimals, then to int
            return int(float(cleaned)) if cleaned else 0
        except (ValueError, TypeError):
            return 0
