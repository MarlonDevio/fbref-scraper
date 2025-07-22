from curl_cffi import request, requests
from bs4 import BeautifulSoup
import lxml.html
from lxml.html import HtmlElement
import time

# Big 5 leagues
URL = "https://fbref.com/en/comps/#all_comps_club"
BASE_URL = "https://fbref.com"
COMPS_ENDPOINT = "/en/comps"

ID_COMPS_DIV_CONTAINER = '//div[@id="div_comps_club"]'
TH_LEAGUE_NAME = ID_COMPS_DIV_CONTAINER + '//th[@data-stat="league_name"]'
LEAGUE_ANCHOR = TH_LEAGUE_NAME + "//a"
LEAGUE_ANCHOR_URL = LEAGUE_ANCHOR + "/@href"


def sleep_6_seconds():
    time.sleep(6)


def in_xpath(xpath_def: str, content: HtmlElement):
    return content.xpath(xpath_def)


def fetch_data(url) -> HtmlElement | None:
    try:
        response = requests.get(url, impersonate="chrome120")
        response.raise_for_status()
        tree = lxml.html.fromstring(response.text)
        return tree
    except Exception as e:
        print("Failed", e)


data = fetch_data(BASE_URL + COMPS_ENDPOINT)
xp = in_xpath(LEAGUE_ANCHOR, data)
print(xp)

# SEASONS_URLS = {
#     "2122": "https://fbref.com/en/players/6afaebf2/scout/11160/Bryan-Mbeumo-Scouting-Report",
#     "2223": "https://fbref.com/en/players/6afaebf2/scout/11566/Bryan-Mbeumo-Scouting-Report",
#     "2324": "https://fbref.com/en/players/6afaebf2/scout/12192/Bryan-Mbeumo-Scouting-Report",
#     # This will probably 404, but we'll test it anyway
#     "2425": "https://fbref.com/en/players/6afaebf2/scout/12524/Bryan-Mbeumo-Scouting-Report",
# }
#
#
# def save_to_file(filename: str, data: str | bytes) -> None:
#     with open(filename, "w", encoding="utf-8") as file:
#         file.write(data)
#
#
# # --- Main Execution ---
# if __name__ == "__main__":
#     for season, url in SEASONS_URLS.items():
#         print(f"Scraping scouting report for season {season}...")
#
#         # Use curl_cffi's requests, impersonating a Chrome browser
#         # This spoofs the TLS fingerprint, which is often the cause of blocks.
#         try:
#             response = requests.get(url, impersonate="chrome110")
#             response.raise_for_status()  # Check for 4xx/5xx errors
#
#             soup = BeautifulSoup(response.content, "lxml")
#             scouting_report_section = soup
#
#             if scouting_report_section:
#                 save_to_file(
#                     f"scouting_report_{season}.html", scouting_report_section.prettify()
#                 )
#                 print(f"Successfully saved report for season {season}.")
#             else:
#                 print(f"Report section not found for season {season}.")
#
#         except Exception as e:
#             print(f"Failed to retrieve report for season {season}. Error: {e}")
#
#         print("Waiting for 3 seconds...")
#         time.sleep(3)
