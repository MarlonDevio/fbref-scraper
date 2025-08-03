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
    first_name = scrapy.Field()
    last_name = scrapy.Field()
    date_of_birth = scrapy.Field()
    position = scrapy.Field()
    nationality = scrapy.Field()
    club = scrapy.Field()
    url = scrapy.Field()


class ClubItem(scrapy.Item):
    club_id = scrapy.Field()
    name = scrapy.Field()
    country = scrapy.Field()
    league = scrapy.Field()
    season = scrapy.Field()
    url = scrapy.Field()
    players_count = scrapy.Field()


class CompetitionItem(scrapy.Item):
    competition_id = scrapy.Field()
    name = scrapy.Field()
    country = scrapy.Field()
    tier = scrapy.Field()
    url = scrapy.Field()
    seasons = scrapy.Field()


class SeasonItem(scrapy.Item):
    season_id = scrapy.Field()
    year = scrapy.Field()
    competition = scrapy.Field()
    competition_url = scrapy.Field()
    url = scrapy.Field()
    clubs = scrapy.Field()


class PlayerStatsItem(scrapy.Item):
    player_id = scrapy.Field()
    season = scrapy.Field()
    club = scrapy.Field()
    league = scrapy.Field()
    position = scrapy.Field()
    matches_played = scrapy.Field()
    goals = scrapy.Field()
    assists = scrapy.Field()
    yellow_cards = scrapy.Field()
    red_cards = scrapy.Field()
    minutes_played = scrapy.Field()
    url = scrapy.Field()
