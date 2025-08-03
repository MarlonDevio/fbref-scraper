import re
from itemadapter import ItemAdapter


class CleaningPipeline:
    """Pipeline for cleaning and normalizing scraped data."""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Clean text fields by stripping whitespace and normalizing
        text_fields = ['name', 'first_name', 'last_name', 'country', 'league', 
                      'nationality', 'club', 'position', 'competition']
        
        for field in text_fields:
            if adapter.get(field):
                # Strip whitespace and normalize spaces
                adapter[field] = re.sub(r'\s+', ' ', str(adapter[field]).strip())
        
        # Clean URLs
        if adapter.get('url'):
            adapter['url'] = adapter['url'].strip()
            
        # Clean numeric fields
        numeric_fields = ['goals', 'assists', 'yellow_cards', 'red_cards', 
                         'matches_played', 'minutes_played', 'players_count']
        
        for field in numeric_fields:
            if adapter.get(field):
                # Remove non-numeric characters and convert to int
                cleaned_value = re.sub(r'[^\d]', '', str(adapter[field]))
                adapter[field] = int(cleaned_value) if cleaned_value else 0
        
        # Clean IDs (extract from URLs if needed)
        id_fields = ['player_id', 'club_id', 'competition_id', 'season_id']
        for field in id_fields:
            if adapter.get(field) and isinstance(adapter[field], str):
                # Extract ID from URL pattern if it looks like a URL
                if adapter[field].startswith('http'):
                    id_match = re.search(r'/([a-fA-F0-9-]+)/', adapter[field])
                    if id_match:
                        adapter[field] = id_match.group(1)
        
        return item