#!/usr/bin/env python3
from typing import Tuple
import re

from dotenv.variables import Literal

"""
Main runner script for FBRef scraper spiders.
Provides easy commands to run different spiders and manage the scraping process.
"""
import json
import sys
import subprocess
from pathlib import Path
import jsonlines
import requests

urls = [
    "https://www.fbref.com/en/comps/9/2024-2025/2024-2025-Premier-League-Stats",
    "https://www.fbref.com/en/comps/12/2024-2025/2024-2025-La-Liga-Stats",
    "https://www.fbref.com/en/comps/11/2024-2025/2024-2025-Serie-A-Stats",
    "https://www.fbref.com/en/comps/20/2024-2025/2024-2025-Bundesliga-Stats",
    "https://www.fbref.com/en/comps/13/2024-2025/2024-2025-Ligue-1-Stats",
]


def _extract_season_and_league(url: str) -> dict[str, str]:
    d = {}
    pattern = r"https:\/\/w{3}.fbref.com\/en\/comps\/\d+\/\d{4}-\d{4}\/(\d{4}-\d{4}).([A-Za-z\-\d?]+)-Stats"
    match = re.search(pattern, url)
    if match:
        d["season"] = match.group(1)
        d["league"] = match.group(2)
    return d

for url in urls:
    u = _extract_season_and_league(url)
    print(u["league"])


