"""wildfile.app"""
import streamlit as st
from services.weather import fetch_weather
from services.modis import fetch_modis
from services.fire import fetch_fire_last_7
from services.features import update_history

LAT, LON = 34.05, -118.25  # Los Angeles test

st.title("Wildfire Live Feature Dashboard (California)")

weather = fetch_weather(LAT, LON)
modis = fetch_modis(LAT, LON)
fire_last_7 = fetch_fire_last_7(LAT, LON)

row = {**weather, **modis, "fire_last_7": fire_last_7}
df_hist = update_history(row)

latest = df_hist.iloc[-1]

st.subheader("Live Environmental Data")
st.json(latest.to_dict())

st.subheader("Rolling 7-Day History")
st.dataframe(df_hist)

st.subheader("Derived Features")
st.metric("TEMP_RANGE", round(latest["TEMP_RANGE"], 2))
st.metric("dryness", round(latest["dryness"], 2))
st.metric("roll_precip_7", round(latest["roll_precip_7"], 2))
st.metric("roll_wind_7", round(latest["roll_wind_7"], 2))
