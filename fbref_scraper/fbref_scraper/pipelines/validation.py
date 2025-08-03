from scrapy.exceptions import DropItem
from itemadapter import ItemAdapter


class ValidationPipeline:
    """Pipeline for validating scraped data."""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Get item type name
        item_type = type(item).__name__
        
        # Validate based on item type
        if item_type == 'PlayerItem':
            self._validate_player_item(adapter)
        elif item_type == 'ClubItem':
            self._validate_club_item(adapter)
        elif item_type == 'CompetitionItem':
            self._validate_competition_item(adapter)
        elif item_type == 'SeasonItem':
            self._validate_season_item(adapter)
        elif item_type == 'PlayerStatsItem':
            self._validate_player_stats_item(adapter)
        
        return item
    
    def _validate_player_item(self, adapter):
        """Validate player item fields."""
        required_fields = ['player_id', 'url']
        for field in required_fields:
            if not adapter.get(field):
                raise DropItem(f"Missing required field: {field}")
        
        # Validate URL format
        if not adapter.get('url', '').startswith('http'):
            raise DropItem(f"Invalid URL format: {adapter.get('url')}")
    
    def _validate_club_item(self, adapter):
        """Validate club item fields."""
        required_fields = ['club_id', 'name', 'url']
        for field in required_fields:
            if not adapter.get(field):
                raise DropItem(f"Missing required field: {field}")
    
    def _validate_competition_item(self, adapter):
        """Validate competition item fields."""
        required_fields = ['competition_id', 'name', 'url']
        for field in required_fields:
            if not adapter.get(field):
                raise DropItem(f"Missing required field: {field}")
    
    def _validate_season_item(self, adapter):
        """Validate season item fields."""
        required_fields = ['season_id', 'year', 'url']
        for field in required_fields:
            if not adapter.get(field):
                raise DropItem(f"Missing required field: {field}")
    
    def _validate_player_stats_item(self, adapter):
        """Validate player stats item fields."""
        required_fields = ['player_id', 'season', 'url']
        for field in required_fields:
            if not adapter.get(field):
                raise DropItem(f"Missing required field: {field}")
        
        # Validate numeric fields are actually numeric
        numeric_fields = ['goals', 'assists', 'yellow_cards', 'red_cards', 
                         'matches_played', 'minutes_played']
        for field in numeric_fields:
            if adapter.get(field) is not None:
                try:
                    int(adapter[field])
                except (ValueError, TypeError):
                    raise DropItem(f"Invalid numeric value for {field}: {adapter.get(field)}")