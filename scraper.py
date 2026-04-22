import requests
from bs4 import BeautifulSoup
import re


def scrape_top_rated(location: str, cuisine: str):
    
    search_query = f"best {cuisine} restaurants in {location} tripadvisor yelp"
    url = f"https://www.bing.com/search?q={search_query.replace(' ', '+')}"

   
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        results = []

       
        items = soup.find_all('li', class_='b_algo')

        for item in items:
            title_elem = item.find('h2')
            if not title_elem:
                continue

            name = title_elem.get_text().strip()

            name = re.sub(r'^(10|Top|Best|The \d+).+?Restaurants in.+? - ', '', name, flags=re.IGNORECASE)
            name = name.split('|')[0].split('-')[0].strip()

            snippet_elem = item.find(['p', 'div', 'span'], class_=['b_caption', 'st'])
            snippet = snippet_elem.get_text() if snippet_elem else "Highly rated local spot."

      
            rating_match = re.search(r'(\d\.\d|\d)/5', snippet)
            rating = float(rating_match.group(1)) if rating_match else 4.2

           
            if any(word in name.lower() for word in ["tripadvisor", "yelp", "best restaurants", "top 10"]):
                continue

            results.append({
                "name": name,
                "rating": rating,
                "description": snippet[:150] + "...",
                "source": "Web Intelligence"
            })

            if len(results) >= 5:
                break

        return results

    except Exception as e:
        print(f"Scraper Error: {e}")
        
        return []
