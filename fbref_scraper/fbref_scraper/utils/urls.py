from enum import Enum


class League(Enum):
    PREMIER_LEAGUE = ("Premier-League", "9")
    LA_LIGA = ("La-Liga", "12")
    LIGUE_1 = ("Ligue-1", "13")
    BUNDESLIGA = ("Bundesliga", "20")
    SERIE_A = ("Serie-A", "11")

    def __init__(self, path: str, id_league: str):
        self.full_name = path
        self.id = id_league


def get_leagues_history_url(league_name: str, league_id: str) -> str:
    return f"https://fbref.com/en/comps/{league_id}/history/{league_name}-Seasons"


def get_league_years_url(league_name: str, league_id: str, season: str) -> str :
    """
    Raises:
        ValueError: If Season format not YYYY-YYYY
    """
    if not "-" in season or not len(season) == 9:
        raise ValueError("Invalid season. Must be in format YYYY-YYYY")

    return f"https://fbref.com/en/comps/{league_id}/{season}/{season}-{league_name}-Stats"


def league_urls():
    urls = {}
    for league in League:
        league_name = league.full_name
        league_id = league.id
        urls[league_name] = get_league_years_url(league_name, league_id, "2024-2025")
    return urls

def get_squad_id(squad_id: str) -> str:
    

print(league_urls())
"https://fbref.com/en/squads/b8fd03ef/2024-2025/Manchester-City-Stats"