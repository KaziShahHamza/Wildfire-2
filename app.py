"""wildfile.app"""
import streamlit as st
import pandas as pd

from services.weather import fetch_weather_forecast
from services.modis import fetch_modis
from services.fire import fetch_fire_last_7
from services.features import update_history
from services.model import predict_fire

LAT, LON = 34.05, -118.25  # Los Angeles test

st.title("Wildfire 3-Day Forecast (Los Angeles)")

# -------------------------
# Fetch static environmental data
# -------------------------
modis = fetch_modis(LAT, LON)
fire_last_7 = fetch_fire_last_7(LAT, LON)

# -------------------------
# Fetch 3-day weather forecast
# -------------------------
forecast = fetch_weather_forecast(LAT, LON, days=3)  # list of dicts

# Load existing history
try:
    df_hist = pd.read_csv("data_store/history.csv")
except:
    df_hist = pd.DataFrame()

predictions = []

for day in forecast:
    # Combine features
    row = {
        **day,
        **modis,
        "fire_last_7": fire_last_7
    }
    # Update rolling features based on history + forecast
    df_temp = update_history(row)
    latest = df_temp.iloc[-1]

    # Predict wildfire probability
    prob = predict_fire(latest.to_dict())

    # Compute simple confidence
    confidence = 1 - abs(0.5 - prob) * 2  # 1=high confidence (extreme), 0=low confidence (near 0.5)

    predictions.append({
        "DATE": latest["DATE"],
        "PROB": prob,
        "CONFIDENCE": confidence
    })

# -------------------------
# Display Forecast Table
# -------------------------
st.subheader("Wildfire Probability Forecast (Next 3 Days)")

forecast_df = pd.DataFrame(predictions)
forecast_df["PROB_PERCENT"] = (forecast_df["PROB"] * 100).round(1)
forecast_df["CONF_PERCENT"] = (forecast_df["CONFIDENCE"] * 100).round(0)

for idx, row in forecast_df.iterrows():
    prob = row["PROB"]
    conf = row["CONFIDENCE"]

    # Show probability metric
    st.metric(
        label=f"{row['DATE']}",
        value=f"{row['PROB_PERCENT']}%",
        delta=f"Confidence: {row['CONF_PERCENT']}%"
    )

    # Progress bar
    st.progress(min(prob, 1.0))

    # Risk band
    if prob < 0.25:
        st.success("Risk Level: Low")
    elif prob < 0.5:
        st.warning("Risk Level: Moderate")
    else:
        st.error("Risk Level: High")

# Disclaimer
st.caption(
    "Wildfire probability is model-based and estimated using weather forecasts, "
    "historical MODIS satellite data, and recent fire history. "
    "Predictions for future days are approximations and should not be used as a guarantee. "
    "Confidence indicates how extreme the prediction is (higher confidence near very low or very high probabilities)."
)

# -------------------------
# Optional: show latest environment data
# -------------------------
st.subheader("Latest Environmental Data (Most Recent Observations)")
if not df_hist.empty:
    latest_obs = df_hist.iloc[-1]
    st.json(latest_obs.to_dict())

st.subheader("Derived Features (Rolling / Computed Metrics)")
if not df_hist.empty:
    st.dataframe(df_hist)
