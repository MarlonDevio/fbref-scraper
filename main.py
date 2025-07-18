# import requests  # More idiomatic import
# import time
# from bs4 import BeautifulSoup
#
# """
# This project will be about scraping very detailed stats about premier league players
# The main source of data will be from https://fbref.com/
#
# As a small test project, we will first scrape the scouting report of Bryan Mbeumo for
# the seasons 2021-2022 to 2024-2025. In total 4 seasons.
# """
#
# # CONSTANTS
# BASE_URL = "https://fbref.com"
# SEASONS_URLS = {
#     "2122": f"{BASE_URL}/en/players/6afaebf2/scout/11160/Bryan-Mbeumo-Scouting-Report",
#     "2223": f"{BASE_URL}/en/players/6afaebf2/scout/11566/Bryan-Mbeumo-Scouting-Report",
#     "2324": f"{BASE_URL}/en/players/6afaebf2/scout/12192/Bryan-Mbeumo-Scouting-Report",
#     # Note: This URL will likely fail with a 404 until the season starts and data is available.
#     "2425": f"{BASE_URL}/en/players/6afaebf2/scout/12524/Bryan-Mbeumo-Scouting-Report",
# }
#
# # Use more comprehensive headers to mimic a real browser
# HEADERS = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Accept-Language": "en-US,en;q=0.9",
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
# }
#
#
# def save_to_file(filename: str, data: str) -> None:
#     """Saves data to a file. Overwrites if it exists."""
#     # The 'with' statement automatically handles closing the file.
#     with open(filename, "w", encoding="utf-8") as file:
#         file.write(data)
#
#
# def scrape_scouting_report(url: str) -> str | None:
#     """Scrapes the scouting report from a given FBref URL."""
#     try:
#         # Use requests.get() and pass the headers
#         response = requests.get(url, headers=HEADERS)
#
#         # This will raise an HTTPError if the status code is 4xx or 5xx
#         response.raise_for_status()
#
#         soup = BeautifulSoup(response.content, "lxml")
#         scouting_report_section = soup.find("div", {"id": "scouting-report"})
#
#         if not scouting_report_section:
#             print(f"Warning: Scouting report section not found on page {url}")
#             return None
#
#         return scouting_report_section.text.strip()
#
#     except requests.exceptions.HTTPError as e:
#         # Specifically handle HTTP errors like 403 Forbidden or 404 Not Found
#         print(f"HTTP Error fetching {url}: {e}")
#         return None
#     except requests.exceptions.RequestException as e:
#         # Handle other network-related errors (e.g., DNS failure, connection refused)
#         print(f"Error fetching data from {url}: {e}")
#         return None
#
#
# report = scrape_scouting_report(
#     "https://fbref.com/en/players/6afaebf2/scout/12524/Bryan-Mbeumo-Scouting-Report"
# )
# print(report)
# # --- Main Execution ---
# # if __name__ == "__main__":
# #     for season, url in SEASONS_URLS.items():
# #         print(f"Scraping scouting report for season {season}...")
# #         report = scrape_scouting_report(url)
# #
# #         if report:
# #             save_to_file(f"scouting_report_{season}.txt", report)
# #             print(f"Successfully saved report for season {season}.")
# #         else:
# #             print(f"Failed to retrieve or find report for season {season}.")
# #
# #         # Be a good web citizen! Wait before the next request.
# #         print("Waiting for 3 seconds...")
# #         time.sleep(3)
from curl_cffi import requests
from bs4 import BeautifulSoup
import time

SEASONS_URLS = {
    "2122": "https://fbref.com/en/players/6afaebf2/scout/11160/Bryan-Mbeumo-Scouting-Report",
    "2223": "https://fbref.com/en/players/6afaebf2/scout/11566/Bryan-Mbeumo-Scouting-Report",
    "2324": "https://fbref.com/en/players/6afaebf2/scout/12192/Bryan-Mbeumo-Scouting-Report",
    # This will probably 404, but we'll test it anyway
    "2425": "https://fbref.com/en/players/6afaebf2/scout/12524/Bryan-Mbeumo-Scouting-Report",
}


def save_to_file(filename: str, data: str | bytes) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        file.write(data)


# --- Main Execution ---
if __name__ == "__main__":
    for season, url in SEASONS_URLS.items():
        print(f"Scraping scouting report for season {season}...")

        # Use curl_cffi's requests, impersonating a Chrome browser
        # This spoofs the TLS fingerprint, which is often the cause of blocks.
        try:
            response = requests.get(url, impersonate="chrome110")
            response.raise_for_status()  # Check for 4xx/5xx errors

            soup = BeautifulSoup(response.content, "lxml")
            scouting_report_section = soup

            if scouting_report_section:
                save_to_file(
                    f"scouting_report_{season}.html", scouting_report_section.prettify()
                )
                print(f"Successfully saved report for season {season}.")
            else:
                print(f"Report section not found for season {season}.")

        except Exception as e:
            print(f"Failed to retrieve report for season {season}. Error: {e}")

        print("Waiting for 3 seconds...")
        time.sleep(3)
