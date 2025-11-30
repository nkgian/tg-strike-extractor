from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def geocode_location(location_name, timeout=10):
    """
    Takes a location name and returns its latitude and longitude coordinates
    using the Nominatim geocoding service.
    """
    try:
        geolocator = Nominatim(user_agent="tg-strike-extractor")
        
        print(f"Searching for: {location_name}...")
        
        location = geolocator.geocode(location_name, timeout=timeout)

        if location:
            print("-" * 30)
            print(f"Location: {location.address}")
            print(f"Latitude: {location.latitude}")
            print(f"Longitude: {location.longitude}")
            print("-" * 30)
            return location.latitude, location.longitude
        else:
            print(f"Error: Could not find coordinates for '{location_name}'.")
            return None, None
            
    except GeocoderTimedOut:
        print("Error: Geocoding service timed out.")
    except GeocoderServiceError as e:
        print(f"Error: Geocoding service error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    return None, None

# debug
if __name__ == "__main__":
    x = geocode_location("Tikkurila, Vantaa")
    # print latitude
    print(x[0])
