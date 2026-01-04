"""wildfile.app"""
import streamlit as st

from services.weather import fetch_weather
from services.modis import fetch_modis
from services.fire import fetch_fire_last_7
from services.features import update_history
from services.model import predict_fire

LAT, LON = 34.05, -118.25  # Los Angeles test

st.title("Wildfire Live Feature Dashboard (California)")

# -------------------------
# Fetch live data
# -------------------------
weather = fetch_weather(LAT, LON)
modis = fetch_modis(LAT, LON)
fire_last_7 = fetch_fire_last_7(LAT, LON)

row = {**weather, **modis, "fire_last_7": fire_last_7}
df_hist = update_history(row)

latest = df_hist.iloc[-1]

# -------------------------
# 🔥 Wildfire Prediction
# -------------------------
prob = predict_fire(latest.to_dict())

st.subheader("Wildfire Prediction (Next 24–72 Hours)")
st.metric(
    label="Fire Probability",
    value=f"{prob * 100:.1f}%"
)

st.progress(min(prob, 1.0))

# Optional risk band (clean + explainable)
if prob < 0.25:
    st.success("Risk Level: Low")
elif prob < 0.5:
    st.warning("Risk Level: Moderate")
else:
    st.error("Risk Level: High")

st.caption(
    "Probability is model-based and not a guarantee. "
    "Use for situational awareness only."
)

# -------------------------
# Live data sections
# -------------------------
st.subheader("Live Environmental Data")
st.json(latest.to_dict())

st.subheader("Rolling 7-Day History")
st.dataframe(df_hist)

st.subheader("Derived Features")
st.metric("TEMP_RANGE", round(latest["TEMP_RANGE"], 2))
st.metric("dryness", round(latest["dryness"], 2))
st.metric("roll_precip_7", round(latest["roll_precip_7"], 2))
st.metric("roll_wind_7", round(latest["roll_wind_7"], 2))
