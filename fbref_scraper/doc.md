base = "https://fbref.com/en/comps"
prem_stats = "https://fbref.com/en/comps/9/Premier-League-Stats"
urls_table_top_5 = "//table[@id='comps_club']"

urls_comps_xpath = '//table[@id="comps_club"]//th[contains(@class, "left")]'

season_year_table = "//table[@id='seasons']"

teams_table_div_id = "//div[contains(@id, 'switcher_results')]"

regex_url_teams = r"https:\/\/fbref.com\/en\/squads\/.+\/\w.+-?-?-[sS]tats$"

players_table_xpath_stats = "//div[contains(@id, 'div_stats_standard')]"

return f"//a[not(re:test(@href, '{regex_pattern}', 'i'))]/@href"
return f"//a[re:test(@href, '{regex_pattern}', 'i')]/@href"


# Comps stats page
//table[contains(@id, "overall")] => targets the table containing the clubs and their stats

//table[contains(@id, "overall")]//td[contains(@class, "left") and contains(@data-stat, "team")]//a => targets the urls of the clubs

# On the club page (squads)
//table[contains(@id, "standard")] => targets the table of the players stats

//table[contains(@id, "standard")]//th[contains(@class, "left") and contains(@data-stat, "player")]//a => targets the players urls
