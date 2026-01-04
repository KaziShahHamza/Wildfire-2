import requests
from datetime import datetime, timedelta

def fetch_weather(lat, lon):
    """
    Fetch today's weather (same as before)
    """
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

    precip_mm = r["daily"]["precipitation_sum"][0]
    tmax_c = r["daily"]["temperature_2m_max"][0]
    tmin_c = r["daily"]["temperature_2m_min"][0]
    wind_kmh = r["daily"]["wind_speed_10m_max"][0]

    precip_in = precip_mm / 25.4
    tmax_f = (tmax_c * 9/5) + 32
    tmin_f = (tmin_c * 9/5) + 32
    wind_mph = wind_kmh * 0.621371

    return {
        "DATE": date,
        "PRECIPITATION": round(precip_in, 3),
        "MAX_TEMP": round(tmax_f, 2),
        "MIN_TEMP": round(tmin_f, 2),
        "AVG_WIND_SPEED": round(wind_mph, 2),
        "DAY_OF_YEAR": dt.timetuple().tm_yday,
        "MONTH": dt.month
    }


def fetch_weather_forecast(lat, lon, days=3):
    """
    Fetch a multi-day weather forecast (default 3 days)
    Returns a list of dicts compatible with wildfire prediction
    """
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
        "forecast_days": days,
        "timezone": "America/Los_Angeles"
    }

    r = requests.get(url, params=params).json()

    forecast_list = []
    for i in range(days):
        date = r["daily"]["time"][i]
        dt = datetime.fromisoformat(date)

        precip_mm = r["daily"]["precipitation_sum"][i]
        tmax_c = r["daily"]["temperature_2m_max"][i]
        tmin_c = r["daily"]["temperature_2m_min"][i]
        wind_kmh = r["daily"]["wind_speed_10m_max"][i]

        precip_in = precip_mm / 25.4
        tmax_f = (tmax_c * 9/5) + 32
        tmin_f = (tmin_c * 9/5) + 32
        wind_mph = wind_kmh * 0.621371

        forecast_list.append({
            "DATE": date,
            "PRECIPITATION": round(precip_in, 3),
            "MAX_TEMP": round(tmax_f, 2),
            "MIN_TEMP": round(tmin_f, 2),
            "AVG_WIND_SPEED": round(wind_mph, 2),
            "DAY_OF_YEAR": dt.timetuple().tm_yday,
            "MONTH": dt.month
        })

    return forecast_list
