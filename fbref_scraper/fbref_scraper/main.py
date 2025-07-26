import jsonlines

with jsonlines.open("./data/history_league_urls.jsonl") as reader:
    for item in reader:
        json_obj = dict(item)
        for key in json_obj:
            print(json_obj[key])
