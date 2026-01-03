"""wildfile.services.fire"""
import pandas as pd

FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api/country/csv/USA/7"

def fetch_fire_last_7(lat, lon, radius_deg=0.25):
    """
    Returns number of fire detections within ~25km
    in the last 7 days around (lat, lon)
    """

    df = pd.read_csv(FIRMS_URL)

    if "latitude" not in df.columns or "longitude" not in df.columns:
        return 0

    nearby = df[
        (abs(df["latitude"] - lat) <= radius_deg) &
        (abs(df["longitude"] - lon) <= radius_deg)
    ]

    return int(len(nearby))
