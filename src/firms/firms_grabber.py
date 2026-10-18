import io
import math

import pandas as pd
import requests

from src.settings import FIRMS_API_KEY

SOURCES = ["VIIRS_NOAA20_NRT", "VIIRS_SNPP_NRT", "MODIS_NOAA20_NRT", "MODIS_SNPP_NRT"]

def get_bounding_box(lat, lon, radius_km):
    """
    Calculates a square bounding box around a point for the API query.
    """
    # approx conversions for 1 degree of latitude/longitude
    lat_degree_km = 111.0
    lon_degree_km = 111.0 * math.cos(math.radians(lat))
    
    lat_offset = radius_km / lat_degree_km
    lon_offset = radius_km / lon_degree_km
    
    return f"{lon - lon_offset},{lat - lat_offset},{lon + lon_offset},{lat + lat_offset}"

def fetch_fires(lat, lon, radius_km=50, day_range=1):
    """
    Queries NASA FIRMS for fires within a radius of a location.
    Iterates through multiple satellite sources.
    """
    if not FIRMS_API_KEY:
        print("[NOTE]: FIRMS_API_KEY is not set. Add it to the .env file inside your virtual environment.")
        return None

    bbox = get_bounding_box(lat, lon, radius_km)
    all_data_frames = []
    
    print(f"Querying NASA FIRMS for area: {bbox}")

    for source in SOURCES:
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{FIRMS_API_KEY}/{source}/{bbox}/{day_range}"
        
        print(f"Connecting to {source}...")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"Error {response.status_code} from {source}: {response.text}")
                continue
            
            csv_data = response.text
            
            # check if empty
            if not csv_data or csv_data.strip() == "":
                continue

            df = pd.read_csv(io.StringIO(csv_data))
            # ensure satellite source is a column
            df['satellite_source'] = source
            all_data_frames.append(df)

        except Exception as e:
            print(f"Connection failed for {source}: {e}")
            continue

    if not all_data_frames:
        return None

    return pd.concat(all_data_frames, ignore_index=True)
