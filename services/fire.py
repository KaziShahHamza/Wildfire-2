"""wildfile.services.fire"""
import pandas as pd
import os

FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api/country/csv/USA/7"
DATA_STORE = "data_store"

# Make sure the data_store folder exists
os.makedirs(DATA_STORE, exist_ok=True)

def fetch_fire_last_7(lat, lon, radius_deg=0.25, city_name="city"):
    """
    Returns number of fire detections within ~25km
    in the last 7 days around (lat, lon)
    Also saves the filtered fire data to data_store folder
    """

    # Fetch FIRMS CSV
    df = pd.read_csv(FIRMS_URL)

    # Check for required columns
    if "latitude" not in df.columns or "longitude" not in df.columns:
        return 0

    # Filter nearby fires
    nearby = df[
        (abs(df["latitude"] - lat) <= radius_deg) &
        (abs(df["longitude"] - lon) <= radius_deg)
    ]

    # Save to CSV
    city_filename = city_name.replace(" ", "_")
    file_path = os.path.join(DATA_STORE, f"fire_last_7_{city_filename}.csv")
    nearby.to_csv(file_path, index=False)

    return int(len(nearby))
