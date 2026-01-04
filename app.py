"""wildfile.app"""
import streamlit as st
import pandas as pd

from services.weather import fetch_weather_forecast
from services.modis import fetch_modis
from services.fire import fetch_fire_last_7
from services.features import update_history
from services.model import predict_fire
import os

# -------------------------
# Cities to predict
# -------------------------
CITIES = {
    "Los Angeles": (34.05, -118.25),
    "San Francisco": (37.77, -122.42)
}

st.title("California Wildfire 3-Day Forecast")

for city, (LAT, LON) in CITIES.items():
    st.header(f"{city}")

    # -------------------------
    # Static environmental data
    # -------------------------
    modis = fetch_modis(LAT, LON)
    fire_last_7 = fetch_fire_last_7(LAT, LON)

    # -------------------------
    # 3-day weather forecast
    # -------------------------
    forecast = fetch_weather_forecast(LAT, LON, days=3)
    predictions = []

    for day in forecast:
        row = {**day, **modis, "fire_last_7": fire_last_7}
        df_temp = update_history(row, city=city)
        latest = df_temp.iloc[-1]

        # Predict wildfire probability
        prob = predict_fire(latest.to_dict())
        confidence = 1 - abs(0.5 - prob) * 2

        predictions.append({
            "DATE": latest["DATE"],
            "PROB": prob,
            "CONFIDENCE": confidence
        })

    # -------------------------
    # Display probability forecast
    # -------------------------
    st.subheader("Wildfire Probability Forecast (Next 3 Days)")
    forecast_df = pd.DataFrame(predictions)
    forecast_df["PROB_PERCENT"] = (forecast_df["PROB"] * 100).round(1)
    forecast_df["CONF_PERCENT"] = (forecast_df["CONFIDENCE"] * 100).round(0)

    for idx, row in forecast_df.iterrows():
        prob = row["PROB"]
        conf = row["CONFIDENCE"]

        st.metric(
            label=f"{row['DATE']}",
            value=f"{row['PROB_PERCENT']}%",
            delta=f"Confidence: {row['CONF_PERCENT']}%"
        )

        st.progress(min(prob, 1.0))

        if prob < 0.25:
            st.success("Risk Level: Low")
        elif prob < 0.5:
            st.warning("Risk Level: Moderate")
        else:
            st.error("Risk Level: High")

    # -------------------------
    # Show latest environmental data
    # -------------------------
    st.subheader("Latest Environmental Features")
    # Use the latest row after update_history (rolling features + filled LST_C)
    st.json(latest.to_dict())

    # -------------------------
    # Show city-specific CSV history
    # -------------------------
    st.subheader(f"{city} Historical Data (Rolling Features)")
    csv_file = f"data_store/history_{city.replace(' ', '_')}.csv"
    if os.path.exists(csv_file):
        df_hist = pd.read_csv(csv_file)
        st.dataframe(df_hist)
    else:
        st.info("No history data available yet for this city.")

# -------------------------
# Disclaimer
# -------------------------
st.caption(
    """
    Wildfire probability is estimated using:
    - 3-day weather forecasts (temperature, precipitation, wind)
    - MODIS satellite features (NDVI, EVI, LST)
    - Fire activity in the past 7 days around the city

    Probability indicates the model's estimate of wildfire occurrence (0–100%).  
    Confidence shows extremity of prediction: higher near very low (<25%) or very high (>75%) probabilities.  
    Risk bands:
    - Low (<25%)  
    - Moderate (25–50%)  
    - High (>50%)  

    These predictions are **approximations**, not guarantees.
    """
)
