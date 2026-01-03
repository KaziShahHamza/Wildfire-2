"""wildfile.services.weather"""
import requests
from datetime import datetime

def fetch_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "precipitation_sum",
            "temperature_2m_max",
            "temperature_2m_min",
            "wind_speed_10m_max"
        ],
        "forecast_days": 1,
        "timezone": "America/Los_Angeles"
    }

    r = requests.get(url, params=params).json()

    date = r["daily"]["time"][0]
    dt = datetime.fromisoformat(date)

    # Raw metric values from Open-Meteo
    precip_mm = r["daily"]["precipitation_sum"][0]
    tmax_c = r["daily"]["temperature_2m_max"][0]
    tmin_c = r["daily"]["temperature_2m_min"][0]
    wind_kmh = r["daily"]["wind_speed_10m_max"][0]

    # Unit conversions to match California training data
    precip_in = precip_mm / 25.4
    tmax_f = (tmax_c * 9/5) + 32
    tmin_f = (tmin_c * 9/5) + 32
    wind_mph = wind_kmh * 0.621371

    return {
        "DATE": date,
        "PRECIPITATION": round(precip_in, 3),     # inches
        "MAX_TEMP": round(tmax_f, 2),              # °F
        "MIN_TEMP": round(tmin_f, 2),              # °F
        "AVG_WIND_SPEED": round(wind_mph, 2),      # mph
        "DAY_OF_YEAR": dt.timetuple().tm_yday,
        "MONTH": dt.month
    }
