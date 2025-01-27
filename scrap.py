# ## `Final Code:`

# - See the structure study and output format before this code.
# - The related and main news are both combined in the same list.
# - Two functions are merged into single function with related_news flag.

# 

# ### Getting all news:

# In[40]:


import json
import shutil
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from bs4.element import Comment


# In[ ]:


# Add argument parser to take keyword as input from cmd:
parser = argparse.ArgumentParser()
parser.add_argument("--keyword", help="Keyword to search in news")


# In[3]:


# only for jupyter notebook:
keyword = "adani"


# In[ ]:


# take keyword as input from cmd as --keyword zomato:
args = parser.parse_args()
if args.keyword:
    keyword = args.keyword
else:
    print("No keyword provided. Using default keyword 'zomato'")
    keyword = "zomato"


# In[5]:


link = "https://pulse.zerodha.com"


# In[ ]:


#  Get page:
page = requests.get(link)

if page.status_code != 200:
    raise Exception(f"Failed to fetch page. Status code: {page.status_code}")
else:
    print("Page fetched successfully...")
    
page_content = BeautifulSoup(page.content, 'html.parser')


# In[7]:


def timestamp(filename_safe=True, spaces=False):
    if filename_safe and spaces:
        return datetime.now().strftime("%Y-%m-%d %I-%M-%S %p")
    if filename_safe and not spaces:
        return datetime.now().strftime("%Y-%m-%d_%I-%M-%S_%p")

    return datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

# timestamp()


# In[ ]:


# Save the fetched content in a file:
filename = f"./{timestamp()}_full.html"
with open(filename, "w", encoding="utf-8") as file:
    file.write(page_content.prettify())
print(f'Page content saved to file: "{filename}"')


# In[9]:


# Get the news list:
news_all = page_content.find('ul', attrs={'id': 'news'})
news_items = news_all.find_all('li', attrs={'class': 'box item'})


# In[10]:


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
        news_link = safe_find_attr(news_list_item, 'a', {'class': 'title2'}, 'href')
        news_desc = "" # No description available for similar news
        
    news_date = safe_find_attr(news_list_item, "span", {"class": "date"}, "title")
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


# In[ ]:


final_news_list = []

for news in news_items:
    # print(json.dumps(get_news_content(news), indent=4))
    final_news_list.append(get_news_content(news))
    
    # Check if similar news exist, if yes, append them as separate news items:
    if news.find("ul", attrs={"class": "similar"}):
        # print("Similar news exist. Appending it as separate news item")
        similar_news = news.find("ul", attrs={"class": "similar"}).find_all("li")

        for similar_news_item in similar_news:
            # print(json.dumps(get_news_content(similar_news_item, is_similar_news=True), indent=4))
            final_news_list.append(get_news_content(similar_news_item, is_similar_news=True))

print("\n\nProcessing completed successfully...")
print("Total main news scraped :".rjust(40), len(news_items))
print("Total related news scraped :".rjust(40), len(final_news_list) - len(news_items))
print("Total news scraped :".rjust(40), len(final_news_list))


# In[12]:


# Save the final news list in a file:
filename = f"./{timestamp()}_news.json"
with open(filename, "w", encoding="utf-8") as file:
    json.dump(final_news_list, file, indent=4)


# 

# ### Query News:

# In[13]:


# Find for the keyword in the news list:
keyword = keyword.lower()
keyword_news = []

# Find the keyword in the news list:
for news in final_news_list:
    if keyword in news['data_search'].lower():
        keyword_news.append(news)


# In[ ]:


print("Total news items with keyword :".rjust(40), len(keyword_news), end="\n\n")
print(f'Saved all news in file: "{filename}"')


# In[ ]:


# Save the keyword news list in a file:
filename = f"./{timestamp()}_query.json"
with open(filename, "w", encoding="utf-8") as file:
    json.dump(keyword_news, file, indent=4)
print(f'Saved queried news in file: "{filename}"')


# In[ ]:





# ### Fetching the queries:

# In[16]:


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


# In[17]:


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(string=True)
    visible_texts = filter(tag_visible, texts)

    # Return the non-empty visible texts joined by new line:
    final_text = "\n".join(t.strip() for t in visible_texts if t.strip() != "")
    # final_text = u"\n\n".join(t.strip() for t in visible_texts)
    return final_text


# In[34]:


# Gives only the news content from entire page:
# Uses custom code to remove unwanted tags and text
# Coded as per the html structures of various news sources

def handle_source_wise_news(resp, link) -> str:
    page_content = BeautifulSoup(resp.content, "html.parser")
    if page_content is None:
        return "Could not fetch page content"


    if "economictimes" in link.lower():
        print("\tStep   :> ET article > ", sep="", end="")
        # find div with class="artText medium"
        news_div = page_content.find(
            "div", attrs={"class": ["artText", "medium"]})

        # If div in this pattern is not found, then return full page content:
        # Bcz ET has used different pattern for some news articles
        if news_div is None:
            print("Diff html pattern > Return full page.")
            return text_from_html(page_content.get_text())

        # if news_div found, delete any tag with classes "adBox" or "custom_ad"
        for ad in page_content.find_all(attrs={"class": ["adBox", "custom_ad"]}):
            ad.decompose()
        print("Removed ads > Return News.")

        return text_from_html(news_div.prettify())


    elif "thehindu" in link.lower():
        print("\tStep   :> The-Hindu article > ", sep="", end="")
        # div with class "storyline" has news content
        # real news (without header and all) is div.articlebodycontent
        news_div = page_content.find("div", attrs={"class": "storyline"})

        # If its not found, return full page content (assuming diff html pattern):
        if news_div is None:
            print("Diff html pattern > Return full page.")
            return text_from_html(page_content.get_text())

        # If news found: div.artinrstl-ad div.article-ad div.artmeterpv div.also-read
        for ad in news_div.find_all(attrs={"class": ["artinrstl-ad", "article-ad", "artmeterpv", "also-read", "share-page"]}):
            ad.decompose()
        print("Removed ads > ", sep="", end="")

        # Rm all content after div.article-published-time-end
        cutoff_tag = news_div.find(
            "div", attrs={"class": "article-published-time-end"})
        if cutoff_tag:
            for sibling in list(cutoff_tag.find_all_next()):
                sibling.decompose()
            print("Removed trailing content > ", sep="", end="")

        print("Return News.")
        return text_from_html(news_div.prettify())


    elif "ndtvprofit" in link.lower():
        # This seems complex one, randomly generated ids and classes
        # Approach 1:
        # # main news in div."story-base-template-m__body-container__ZeMOl"
        # # ads: div.story-element-text-also-read responsive-ad
        # Approach 2:
        # find all div."story-element story-element-text"
        # remove ads from these ones using same ad pattern

        print("\tStep   :> NDTV Profit article > ", sep="", end="")
        # Approach 2: find all div."story-element story-element-text"
        news_divs = page_content.find_all(
            "div", attrs={"class": ["story-element", "story-element-text", "key-highlights-wrapper"]})
        if not news_divs:
            print("Diff html pattern > Return full page.")
            return text_from_html(page_content.get_text())

        # If news found: delete div."story-element-text-also-read responsive-ad"
        for news_div in news_divs:
            # for ad in news_div.find_all(attrs={"class": ["story-element-text-also-read", "responsive-ad"]}):
            for ad in news_div.find_all("div", attrs={"class": ["story-element-text-also-read", "responsive-ad", "also-read-container", "also-read-m__bb-opinion-container__V-vnP"]}):
                ad.decompose()

        print("Removed ads > Return News.")
        # put all news divs together and return
        dummy_page = f"<body> {''.join([news_div.prettify() for news_div in news_divs])} </body>"
        return text_from_html(dummy_page)

    # elif "moneycontrol" in link.lower():

    # For any other source, return full page content:
    else:
        return text_from_html(page_content.prettify())


# ### Confirm:
# - The Hindu, NDTV Profit (Bloomberg Quint), and Economic Times are checked.
# - ZeeBiz, MoneyControl, and ?? are not coded and checked.
# 
# ### Test source wise:
# - Do not delete this 👇 cell
# - it is for testing purpose
# - Instead, comment it out

# In[35]:


# link = "https://economictimes.indiatimes.com/markets/expert-view/food-delivery-slowdown-hits-zomato-but-qsr-resilience-could-lead-to-recovery-jignanshu-gor/articleshow/117451126.cms"
# link = "https://www.thehindu.com/business/budget/budget-should-announce-tax-cuts-for-individuals-to-boost-consumption-barclays/article69131051.ece"
# link = "https://www.ndtvprofit.com/quarterly-earnings/q3-results-2025-today-adani-green-adani-energy-solutions-dr-reddys-lab-hpcl-indus-towers-quarterly-earnings-live-blog"

# resp = requests.get(link)
# news_content = handle_source_wise_news(resp, link)
# with open("temp.json", "w", encoding="utf-8") as file:
#     json.dump({"news": news_content}, file, indent=4)
# print(news_content)


# In[36]:


def get_news_article(link) -> tuple[bool, str]:
    try:
        resp = requests.get(link)

        if resp.status_code != 200:
            flag = False
            page_content = ""
        else:
            if resp.content is None:
                flag = False
                page_content = "No content found"
            else:
                flag = True
                page_content = handle_source_wise_news(resp, link)
            # print(page_content)
    except Exception as e:
        flag = False
        page_content = "Error: " + e
    
    finally:
        return flag, page_content
        


# In[ ]:


# Fetch the individual ones:
print()
total, success, fail = len(keyword_news), 0, 0

def wrap(text, offset=15):
    # 15 is calc from "\tLink   :> " length + 1
    t_width = shutil.get_terminal_size().columns
    # IDK why but sometimes, text still overflows, so -10 to be safe
    rem = t_width - offset - 10
    if len(text) > rem:
        return text[: rem] + "..."
    return text


# In[ ]:


for news in keyword_news:
    print(f"\n[{success + fail + 1:02d} / {total:02d}]")
    print(f"\tNews   :> { wrap(news['title']) }")
    print(f"\tFrom   :> { wrap(news['source']) }")
    # print(f"\tLink   :> {news['link']}")
    print(f"\tLink   :> { wrap(news['link']) }")

    flag, content = get_news_article(news['link'])
    if flag:
        print(f"\tStatus :> ✅ Success...")
        success += 1
        news['full_news'] = content
    else:
        print(f"\tStatus :> ❌ Failed...")
        fail += 1
        news['full_news'] = "Failed to fetch news content..."

    # break

print()
print("Queried total :".rjust(40), total)
print("Successful :".rjust(40), success)
print("Failed :".rjust(40), fail)
print()


# In[ ]:


# Save the keyword news list in a file:
filename = f"./{timestamp()}_query_final.json"
with open(filename, "w", encoding="utf-8") as file:
    json.dump(keyword_news, file, indent=4)
print(f'Saved final query results in file: "{filename}"')


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




