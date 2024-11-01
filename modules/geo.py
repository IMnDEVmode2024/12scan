import requests
from time import sleep
from typing import List, Dict, Optional

class GeoLocator:
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': '12scan/1.0 (police scanner analysis tool)'
        }
        self.skip_words = {
            'ai', 'first', 'today', 'end', 'two', 'three', 'years', 'smart',
            'intel', 'spr', 'gis', 'the', 'a', 'an', 'and', 'or', 'but',
            'number', 'numbers', 'day', 'days', 'week', 'weeks', 'month',
            'months', 'year', 'mile', 'miles'
        }

    def _should_geocode(self, location: str) -> bool:
        location = location.lower().strip()
        if location in self.skip_words:
            return False
        if location.replace(' ', '').replace('-', '').isdigit() or len(location) < 3:
            return False
        if location.split()[0].isdigit():
            return False
        if location.replace('-', '').startswith('10') and len(location) <= 5:
            return False
        return True

    def get_location(self, place: str) -> Optional[Dict]:
        if not self._should_geocode(place):
            return None

        params = {
            'q': place,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1,
            'namedetails': 1
        }

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=self.headers,
                    timeout=10
                )

                if response.status_code == 200:
                    results = response.json()
                    if results:
                        result = results[0]
                        location_type = result.get('type', '')
                        if location_type in ['house', 'address']:
                            return None
                            
                        return {
                            'location': place,
                            'latitude': float(result['lat']),
                            'longitude': float(result['lon']),
                            'type': location_type,
                            'importance': float(result.get('importance', 0))
                        }
                elif response.status_code in [429, 503, 502, 504]:
                    sleep(retry_delay * (attempt + 1))
                    continue
                
                return None

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    sleep(retry_delay * (attempt + 1))
                    continue
                print(f"Error finding location for {place}: {str(e)}")
                return None

        return None

    def locate_entities(self, entities: List[Dict]) -> List[Dict]:
        locations = []
        processed = set()
        
        try:
            for entity in entities:
                if entity['type'] in ['GPE', 'LOC', 'FAC']:
                    location = entity['entity'].strip()
                    if location and location not in processed:
                        processed.add(location)
                        result = self.get_location(location)
                        if result and result['importance'] > 0.2:
                            locations.append(result)
                        sleep(1.5)
            
            locations.sort(key=lambda x: x['importance'], reverse=True)
            return locations[:10]
            
        except Exception as e:
            print(f"Error in locate_entities: {str(e)}")
            return locations
