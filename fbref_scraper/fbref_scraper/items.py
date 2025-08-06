# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FbrefScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class PlayerItem(scrapy.Item):
    player_id = scrapy.Field()
    player_name = scrapy.Field()


class CountryItem(scrapy.Item):
    country_id = scrapy.Field()
    country = scrapy.Field()


class ClubItem(scrapy.Item):
    club_id = scrapy.Field()
    club_name = scrapy.Field()


class LeagueItem(scrapy.Item):
    league_id = scrapy.Field()
    league_name = scrapy.Field()
    country_id = scrapy.Field()


__all__ = ["FbrefScraperItem", "PlayerItem", "CountryItem", "ClubItem", "LeagueItem"]
