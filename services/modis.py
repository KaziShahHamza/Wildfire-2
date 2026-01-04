"""wildfile.services.modis"""
import ee
import os
import json
import streamlit as st

# -------------------------
# Initialize Earth Engine with service account from Streamlit Secrets
# -------------------------
if not ee.data._initialized:
    # Load GEE credentials from Streamlit secrets
    gee_creds = st.secrets["GEE"]["credentials"]
    creds_dict = json.loads(gee_creds)

    # Write temporary JSON file for service account
    creds_file = "/tmp/service_account.json"
    with open(creds_file, "w") as f:
        json.dump(creds_dict, f)

    # Initialize EE with service account
    ee.Initialize(ee.ServiceAccountCredentials(
        creds_dict["client_email"], creds_file
    ))

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

    # Convert to meaningful units if values exist
    return {
        "NDVI": ndvi * 0.0001 if ndvi is not None else None,
        "EVI": evi * 0.0001 if evi is not None else None,
        "LST_C": (lst * 0.02 - 273.15) if lst is not None else None
    }
