# Sample use:
# python scrap_final.py --keyword zomato
# python scrap_final.py --keyword birla

import json
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Add argument parser to take keyword as input from cmd:
parser = argparse.ArgumentParser()
parser.add_argument("--keyword", help="Keyword to search in news")

# take keyword as input from cmd as --keyword zomato:
args = parser.parse_args()
if args.keyword:
    keyword = args.keyword
else:
    print("No keyword provided. Using default keyword 'zomato'")
    keyword = "zomato"


link = "https://pulse.zerodha.com"

#  Get page:
page = requests.get(link)

if page.status_code != 200:
    raise Exception(f"Failed to fetch page. Status code: {page.status_code}")
else:
    print("Page fetched successfully...")

page_content = BeautifulSoup(page.content, 'html.parser')


def timestamp(filename_safe=True, spaces=False):
    if filename_safe and spaces:
        return datetime.now().strftime("%Y-%m-%d %I-%M-%S %p")
    if filename_safe and not spaces:
        return datetime.now().strftime("%Y-%m-%d_%I-%M-%S_%p")

    return datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

# timestamp()


# Save the fetched content in a file:
filename = f"./{timestamp()}_full.html"
with open(filename, "w", encoding="utf-8") as file:
    file.write(page_content.prettify())
print(f'Page content saved to file: "{filename}"')


# Get the news list:
news_all = page_content.find('ul', attrs={'id': 'news'})
news_items = news_all.find_all('li', attrs={'class': 'box item'})


# Function to get news content from a news list item:
def get_news_content(news_list_item, is_similar_news=False):
    def safe_find_text(element, tag, attrs):
        element = element.find(tag, attrs)
        return element.text if element else ""

    def safe_find_attr(element, tag, attrs, attr_name):
        element = element.find(tag, attrs)
        return element[attr_name] if element and attr_name in element.attrs else ""

    if not is_similar_news:
        news_title = safe_find_text(news_list_item, 'h2', {'class': 'title'})
        news_link = safe_find_attr(news_list_item, 'a', {}, 'href')
        news_desc = safe_find_text(news_list_item, "div", {"class": "desc"})

    else:
        news_title = safe_find_text(news_list_item, 'a', {'class': 'title2'})
        news_link = safe_find_attr(news_list_item, 'a', {
                                   'class': 'title2'}, 'href')
        news_desc = ""  # No description available for similar news

    news_date = safe_find_attr(news_list_item, "span", {
                               "class": "date"}, "title")
    news_source = safe_find_text(news_list_item, "span", {"class": "feed"})
    news_data_search = f"{news_title} {news_desc}".strip()

    return {
        "title": news_title,
        "link": news_link,
        "description": news_desc,
        "date": news_date,
        "source": news_source,
        "data_search": news_data_search
    }


final_news_list = []

for news in news_items:
    # print(json.dumps(get_news_content(news), indent=4))
    final_news_list.append(get_news_content(news))

    # Check if similar news exist, if yes, append them as separate news items:
    if news.find("ul", attrs={"class": "similar"}):
        # print("Similar news exist. Appending it as separate news item")
        similar_news = news.find(
            "ul", attrs={"class": "similar"}).find_all("li")

        for similar_news_item in similar_news:
            # print(json.dumps(get_news_content(similar_news_item, is_similar_news=True), indent=4))
            final_news_list.append(get_news_content(
                similar_news_item, is_similar_news=True))

print("\n\nProcessing completed successfully...")
print("Total main news scraped :".rjust(40), len(news_items))
print("Total related news scraped :".rjust(40),
      len(final_news_list) - len(news_items))
print("Total news scraped :".rjust(40), len(final_news_list))


# Save the final news list in a file:
filename = f"./{timestamp()}_news.json"
with open(filename, "w", encoding="utf-8") as file:
    json.dump(final_news_list, file, indent=4)


# Find for the keyword in the news list:
keyword = keyword.lower()
keyword_news = []

# Find the keyword in the news list:
for news in final_news_list:
    if keyword in news['data_search'].lower():
        keyword_news.append(news)


print("Total news items with keyword :".rjust(
    40), len(keyword_news), end="\n\n")
print(f'Saved all news in file: "{filename}"')


# Save the keyword news list in a file:
filename = f"./{timestamp()}_query.json"
with open(filename, "w", encoding="utf-8") as file:
    json.dump(keyword_news, file, indent=4)
# print("Saved queried news in file `", f"{timestamp()}_query.json", "`")
print(f'Saved queried news in file: "{filename}"')
