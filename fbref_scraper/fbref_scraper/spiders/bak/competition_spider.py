import scrapy
from scrapy.http import Response, TextResponse
from fbref_scraper.items import CompetitionItem
from fbref_scraper.utils.urls import extract_competition_id


class CompetitionSpider(scrapy.Spider):
    name = "competitions"
    
    start_urls = [
        "https://fbref.com/en/comps/"
    ]
    
    def parse(self, response: Response, **kwargs):
        """
        Parse the main competitions page to extract competition information.
        
        Args:
            response: HTTP response object containing the competitions page
            
        Yields:
            CompetitionItem: Individual competition items
        """
        if not isinstance(response, TextResponse):
            return
            
        # Extract competition URLs using the xpath from doc.md
        competition_links = response.xpath('//table[@id="comps_club"]//th[contains(@class, "left")]//a/@href').getall()
        
        for link in competition_links:
            if link:
                # Convert relative URLs to absolute URLs
                competition_url = response.urljoin(link)
                yield scrapy.Request(
                    url=competition_url,
                    callback=self.parse_competition,
                    meta={'competition_url': competition_url}
                )
    
    def parse_competition(self, response: Response):
        """
        Parse individual competition page to extract detailed information.
        
        Args:
            response: HTTP response object containing the competition page
            
        Yields:
            CompetitionItem: Competition item with detailed information
        """
        if not isinstance(response, TextResponse):
            return
            
        competition_url = response.meta.get('competition_url', response.url)
        
        # Extract competition details
        competition_item = CompetitionItem()
        competition_item['competition_id'] = extract_competition_id(competition_url)
        competition_item['url'] = competition_url
        
        # Extract competition name from page title or header
        name = response.xpath('//h1/text()').get()
        if name:
            competition_item['name'] = name.strip()
        
        # Extract country information if available
        country = response.xpath('//span[contains(@class, "country")]//text()').get()
        if country:
            competition_item['country'] = country.strip()
        
        # Extract tier information if available (from breadcrumb or description)
        tier_text = response.xpath('//div[contains(@class, "meta")]//text()').re_first(r'Tier\s+(\d+)')
        if tier_text:
            competition_item['tier'] = int(tier_text)
        
        # Extract available seasons
        seasons = []
        season_links = response.xpath('//table[@id="seasons"]//th[@data-stat="year_id"]//a')
        for season_link in season_links:
            season_text = season_link.xpath('.//text()').get()
            season_url = season_link.xpath('.//@href').get()
            if season_text and season_url:
                seasons.append({
                    'year': season_text.strip(),
                    'url': response.urljoin(season_url)
                })
        
        competition_item['seasons'] = seasons
        
        yield competition_item
