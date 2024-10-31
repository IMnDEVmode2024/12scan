from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geoapiExercises")

def locate_entities(entities):
    locations = []
    for entity in entities:
        try:
            location = geolocator.geocode(entity['entity'])
            if location:
                locations.append({
                    'location': entity['entity'],
                    'latitude': location.latitude,
                    'longitude': location.longitude
                })
        except Exception as e:
            print(f"Error finding location for {entity['entity']}: {str(e)}")
    return locations