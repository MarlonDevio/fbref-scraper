import psycopg2
from itemadapter import ItemAdapter


class DatabasePipeline:
    """Pipeline for storing items in PostgreSQL database."""
    
    def __init__(self, settings):
        self.settings = settings
        self.connection = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings.get("DATABASE_SETTINGS"))

    def open_spider(self, spider):
        """Initialize database connection when spider opens."""
        try:
            self.connection = psycopg2.connect(**self.settings)
            self.cursor = self.connection.cursor()
            self._create_tables()
            spider.logger.info("Database connection established")
        except Exception as e:
            spider.logger.error(f"Error connecting to database: {e}")

    def close_spider(self, spider):
        """Close database connection when spider closes."""
        if self.connection:
            self.connection.close()
            spider.logger.info("Database connection closed")

    def process_item(self, item, spider):
        """Process and store item in database."""
        if not self.connection:
            spider.logger.warning("No database connection available")
            return item
            
        adapter = ItemAdapter(item)
        item_type = type(item).__name__
        
        try:
            if item_type == 'PlayerItem':
                self._insert_player(adapter)
            elif item_type == 'ClubItem':
                self._insert_club(adapter)
            elif item_type == 'CompetitionItem':
                self._insert_competition(adapter)
            elif item_type == 'SeasonItem':
                self._insert_season(adapter)
            elif item_type == 'PlayerStatsItem':
                self._insert_player_stats(adapter)
            
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            spider.logger.error(f"Error inserting item: {e}")
        
        return item

    def _create_tables(self):
        """Create database tables if they don't exist."""
        # self.cursor.execute("CREATE SCHEMA IF NOT EXISTS testforme")
        tables = {
            'competitions': '''
                CREATE TABLE IF NOT EXISTS competitions (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    country VARCHAR(255),
                    tier INTEGER,
                    url VARCHAR(512) UNIQUE,
                    seasons JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'seasons': '''
                CREATE TABLE IF NOT EXISTS seasons (
                    id VARCHAR(255) PRIMARY KEY,
                    year VARCHAR(50) NOT NULL,
                    competition VARCHAR(255),
                    competition_url VARCHAR(512),
                    url VARCHAR(512) UNIQUE,
                    clubs JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'clubs': '''
                CREATE TABLE IF NOT EXISTS football.clubs (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    country VARCHAR(255),
                    league VARCHAR(255),
                    season VARCHAR(50),
                    url VARCHAR(512) UNIQUE,
                    players_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'players': '''
                CREATE TABLE IF NOT EXISTS players (
                    id VARCHAR(255) PRIMARY KEY,
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    date_of_birth DATE,
                    position VARCHAR(50),
                    nationality VARCHAR(255),
                    club VARCHAR(255),
                    url VARCHAR(512) UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'player_stats': '''
                CREATE TABLE IF NOT EXISTS football.player_stats (
                    id SERIAL PRIMARY KEY,
                    player_id VARCHAR(255) NOT NULL,
                    season VARCHAR(50),
                    club VARCHAR(255),
                    league VARCHAR(255),
                    position VARCHAR(50),
                    matches_played INTEGER,
                    goals INTEGER,
                    assists INTEGER,
                    yellow_cards INTEGER,
                    red_cards INTEGER,
                    minutes_played INTEGER,
                    url VARCHAR(512),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(player_id, season, club)
                )
            '''
        }
        
        for table_name, create_sql in tables.items():
            self.cursor.execute(create_sql)

    def _insert_player(self, adapter):
        """Insert player item into database."""
        sql = '''
            INSERT INTO players (id, first_name, last_name, date_of_birth, position, nationality, club, url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                date_of_birth = EXCLUDED.date_of_birth,
                position = EXCLUDED.position,
                nationality = EXCLUDED.nationality,
                club = EXCLUDED.club,
                url = EXCLUDED.url
        '''
        self.cursor.execute(sql, (
            adapter.get('player_id'),
            adapter.get('first_name'),
            adapter.get('last_name'),
            adapter.get('date_of_birth'),
            adapter.get('position'),
            adapter.get('nationality'),
            adapter.get('club'),
            adapter.get('url')
        ))

    def _insert_club(self, adapter):
        """Insert club item into database."""
        sql = '''
            INSERT INTO football.clubs (id, name, country, league, season, url, players_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                country = EXCLUDED.country,
                league = EXCLUDED.league,
                season = EXCLUDED.season,
                url = EXCLUDED.url,
                players_count = EXCLUDED.players_count
        '''
        self.cursor.execute(sql, (
            adapter.get('club_id'),
            adapter.get('name'),
            adapter.get('country'),
            adapter.get('league'),
            adapter.get('season'),
            adapter.get('url'),
            adapter.get('players_count')
        ))

    def _insert_competition(self, adapter):
        """Insert competition item into database."""
        sql = '''
            INSERT INTO competitions (id, name, country, tier, url, seasons)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                country = EXCLUDED.country,
                tier = EXCLUDED.tier,
                url = EXCLUDED.url,
                seasons = EXCLUDED.seasons
        '''
        import json
        self.cursor.execute(sql, (
            adapter.get('competition_id'),
            adapter.get('name'),
            adapter.get('country'),
            adapter.get('tier'),
            adapter.get('url'),
            json.dumps(adapter.get('seasons', []))
        ))

    def _insert_season(self, adapter):
        """Insert season item into database."""
        sql = '''
            INSERT INTO seasons (id, year, competition, competition_url, url, clubs)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                year = EXCLUDED.year,
                competition = EXCLUDED.competition,
                competition_url = EXCLUDED.competition_url,
                url = EXCLUDED.url,
                clubs = EXCLUDED.clubs
        '''
        import json
        self.cursor.execute(sql, (
            adapter.get('season_id'),
            adapter.get('year'),
            adapter.get('competition'),
            adapter.get('competition_url'),
            adapter.get('url'),
            json.dumps(adapter.get('clubs', []))
        ))

    def _insert_player_stats(self, adapter):
        """Insert player stats item into database."""
        sql = '''
            INSERT INTO player_stats (player_id, season, club, league, position, matches_played, 
                                    goals, assists, yellow_cards, red_cards, minutes_played, url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (player_id, season, club) DO UPDATE SET
                league = EXCLUDED.league,
                position = EXCLUDED.position,
                matches_played = EXCLUDED.matches_played,
                goals = EXCLUDED.goals,
                assists = EXCLUDED.assists,
                yellow_cards = EXCLUDED.yellow_cards,
                red_cards = EXCLUDED.red_cards,
                minutes_played = EXCLUDED.minutes_played,
                url = EXCLUDED.url
        '''
        self.cursor.execute(sql, (
            adapter.get('player_id'),
            adapter.get('season'),
            adapter.get('club'),
            adapter.get('league'),
            adapter.get('position'),
            adapter.get('matches_played'),
            adapter.get('goals'),
            adapter.get('assists'),
            adapter.get('yellow_cards'),
            adapter.get('red_cards'),
            adapter.get('minutes_played'),
            adapter.get('url')
        ))
