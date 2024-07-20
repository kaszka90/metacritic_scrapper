import httpx
import re
from bs4 import BeautifulSoup
import pandas as pd

headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"}
url = 'https://www.metacritic.com/browse/game/pc/all/all-time/metascore/?releaseYearMin=1958&releaseYearMax=2024&platform=pc&page='
counter = 240  # Start from the first page

def check_availability(url, counter):
    print("Checking: " + str(counter))
    url_checked = url + str(counter)
    resp = httpx.get(url_checked, headers=headers)
    html = BeautifulSoup(resp.text, 'html.parser')

    if html.select('.c-navigationPagination_item.c-navigationPagination_item--next.enabled'):
        next_url = url + str(counter + 1)
        return next_url
    else:
        return None

def scrap_page(url, counter):
    url = url + str(counter)    
    resp = httpx.get(url, headers=headers)
    html = BeautifulSoup(resp.text, 'html.parser')
    list_view = html.select('.c-productListings_grid.g-grid-container.u-grid-columns.g-inner-spacing-bottom-large > div')


    scraped_data = []

    for position in list_view:
        title = position.select_one('.c-finderProductCard_titleHeading') # tworzy element title na podstawie wybranej klasy
        release = position.select_one('.u-text-uppercase')   
        score = position.select_one('.c-siteReviewScore > span')
        

        if title and release and score:
            title_text = title.get_text(strip=True)
            release_text = release.get_text(strip=True)
            score_text = score.get_text(strip=True)

            scraped_data.append({
                'Title': title_text,
                'Release Date': release_text,
                'Metascore': score_text
            })

            print(f"Title: {title_text}, Release Date: {release_text}, Metascore: {score_text}")
        else:
            print(f"Failed to scrape data for one of the items. Missing elements.")
    return scraped_data

all_scraped_data = []

while True:
    next_url = check_availability(url, counter)
    if next_url is None:
        print("No more pages.")
        break
    else:
        scraped_data = scrap_page(url, counter)
        all_scraped_data.extend(scraped_data)
        counter += 1  # Increment the counter to go to the next page

df = pd.DataFrame(all_scraped_data)
df.to_csv('scraped_data.csv', index=False)
