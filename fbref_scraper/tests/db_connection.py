import psycopg2
import scrapy
from scrapy.crawler import Crawler
import logging
import os

logger = logging.getLogger(__name__)


class DatabaseConnection:
    def __init__(self, settings) -> None:
        self.settings = settings
        self.connection = None
        self.cursor = None

    def connect_db(self):
        self.connection = psycopg2.connect(**self.settings)
        self.cursor = self.connection.cursor()
        logger.info("Connection succes")

    def get_leagues(self):
        sql = """
        SET SEARCH_PATH TO football;
        SELECT * FROM leagues;
            """
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            id, league, country = row
            print(id)
            print(league)
            print(country)

    def close(self):
        self.cursor.connection.close()


sets = {
    "host": "localhost",
    "user": "myuser",
    "password": "mypassword",
    "database": "mydatabase",
    "port": "5432",
}

d = DatabaseConnection(sets)
d.connect_db()
d.get_leagues()
d.close()
