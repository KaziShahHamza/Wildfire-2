"""wildfile.services.modis"""
import ee
import streamlit as st

# -------------------------
# Initialize Earth Engine for local development
# -------------------------
def initialize_ee():
    try:
        # Always specify your GCP project
        ee.Initialize(project='wildfire-prediction-477513')
    except ee.EEException:
        # Interactive login if needed
        ee.Authenticate()
        ee.Initialize(project='wildfire-prediction-477513')

# Initialize once
initialize_ee()

# -------------------------
# Fetch MODIS features for a point
# -------------------------
def fetch_modis(lat, lon):
    point = ee.Geometry.Point(lon, lat)

    def safe_fetch(collection, band, scale):
        try:
            img = (
                ee.ImageCollection(collection)
                .select(band)
                .filterBounds(point)
                .sort("system:time_start", False)
                .first()
            )
            if img is None:
                return None

            val = img.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=scale
            ).get(band)

            return val.getInfo() if val else None
        except Exception as e:
            st.warning(f"MODIS fetch error for {band}: {e}")
            return None

    ndvi = safe_fetch("MODIS/061/MOD13Q1", "NDVI", 250)
    evi = safe_fetch("MODIS/061/MOD13Q1", "EVI", 250)
    lst = safe_fetch("MODIS/061/MOD11A1", "LST_Day_1km", 1000)

    return {
        "NDVI": ndvi * 0.0001 if ndvi is not None else None,
        "EVI": evi * 0.0001 if evi is not None else None,
        "LST_C": (lst * 0.02 - 273.15) if lst is not None else None
    }
