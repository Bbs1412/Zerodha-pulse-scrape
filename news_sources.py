import json

full_news_json_file = "./2025-01-22_11-28-36_PM_news.json"
with open(full_news_json_file, "r", encoding="utf-8") as file:
    data = json.load(file)

unique_source = []

for news in data:
    link = news["link"]
    link = link.split("/")[2]

    if link not in unique_source:
        unique_source.append(link)

print(f"Unique news sources: {len(unique_source)}")
print(unique_source)