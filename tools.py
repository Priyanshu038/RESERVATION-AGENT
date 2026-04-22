import requests
import asyncio
import random
from bs4 import BeautifulSoup
import scraper  


CUISINES = ['Italian', 'Japanese', 'Mexican', 'Indian', 'French', 'American', 'Thai', 'Mediterranean', 'Vegan']
LOCATIONS = ['Bhubaneswar', 'Cuttack', 'Puri', 'Bhadrak', 'Balasore', 'Rourkela', 'Dhenkanal']


RESTAURANTS = []
RESERVATIONS = []


def initialize_mock_data():
 
    global RESTAURANTS
    for i in range(1, 21):
        RESTAURANTS.append({
            "id": i,
            "name": f"Venue {i}",
            "cuisine": random.choice(CUISINES),
            "rating": round(random.uniform(3.8, 4.9), 1),
            "location": random.choice(LOCATIONS)
        })


initialize_mock_data()




async def search_restaurants_pro_free(criteria):
   
    location_name = criteria.get('location', 'Bhubaneswar')
    cuisine = criteria.get('cuisine', 'restaurant')
    loop = asyncio.get_event_loop()


    try:
        scraped_results = await loop.run_in_executor(
            None, lambda: scraper.scrape_top_rated(location_name, cuisine)
        )
        if len(scraped_results) >= 3:
            return scraped_results
    except Exception as e:
        print(f"Layer 1 (Scraper) Timeout/Error: {e}")
        scraped_results = []


    elements = []
    try:
        geo_url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
        headers = {'User-Agent': 'KhanaDarbaarAgent/2.0'}

        geo_resp = await loop.run_in_executor(None, lambda: requests.get(geo_url, headers=headers).json())
        lat, lon = (geo_resp[0]['lat'], geo_resp[0]['lon']) if geo_resp else ("20.2961", "85.8245")

        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        (node["amenity"="restaurant"](around:5000,{lat},{lon});
         way["amenity"="restaurant"](around:5000,{lat},{lon}););
        out center;"""

        osm_resp = await loop.run_in_executor(
            None, lambda: requests.get(overpass_url, params={'data': overpass_query}, timeout=5).json()
        )
        elements = osm_resp.get('elements', [])
    except Exception as e:
        print(f"Layer 2 (OSM) Error: {e}")


    osm_results = []
    for e in elements[:5]:
        tags = e.get('tags', {})
       
        score = 3.9
        if 'website' in tags: score += 0.4
        if 'phone' in tags: score += 0.3
        if 'opening_hours' in tags: score += 0.2

        osm_results.append({
            "name": tags.get('name', 'Authentic Local Venue'),
            "rating": round(min(score, 5.0), 1),
            "description": f"Located at {tags.get('addr:street', location_name)}",
            "source": "OpenStreetMap"
        })

    final_results = scraped_results + osm_results


    if not final_results:
        return [{
            "name": f"Top Rated {cuisine.capitalize()} Spot",
            "rating": 4.5,
            "description": f"Highly recommended dining in {location_name}",
            "source": "Heuristic System"
        }]

    return final_results[:5]


def make_reservation_logic(details):
 
    res_id = f"RES-{random.randint(1000, 9999)}"

    booking = {
        "id": res_id,
        "restaurant_id": details.get('restaurant_id'),
        "party_size": details.get('party_size'),
        "time": details.get('time'),
        "revenue": random.randint(1500, 5000)  
    }

    RESERVATIONS.append(booking)
    return {
        "success": True,
        "reservation_id": res_id,
        "message": f"Successfully confirmed for {details.get('party_size')} guests at {details.get('time')}."
    }
