"""wildfile.app"""
import streamlit as st
import pandas as pd
import os
import plotly.express as px

from services.weather import fetch_weather_forecast
from services.modis import fetch_modis
from services.fire import fetch_fire_last_7
from services.features import update_history
from services.model import predict_fire

st.set_page_config(page_title="California Wildfire Forecast", layout="wide")
st.title("California Wildfire 3-Day Forecast")

# -------------------------
# Disclaimer
# -------------------------
st.markdown(
    """
    <p style="font-size:14px;">
    Wildfire probability is estimated using:
    <ul>
        <li>3-day weather forecasts (temperature, precipitation, wind)</li>
        <li>MODIS satellite features (NDVI, EVI, LST)</li>
        <li>Fire activity in the past 7 days around the city</li>
    </ul>
    <strong>Probability</strong> indicates the model's estimate of wildfire occurrence (0–100%).<br>
    <strong>Confidence</strong> shows prediction extremity: higher near very low (<25%) or very high (>75%) probabilities.<br>
    <strong>Risk Bands:</strong> Low (<25%), Moderate (25–50%), High (>50%)<br>
    These predictions are <strong>approximations</strong> and should not be used as guarantees.
    </p>
    """,
    unsafe_allow_html=True
)

with st.expander("How Probability and Confidence Are Calculated", expanded=False):
    st.markdown(
        """
        <p style="font-size:14px;">
        The wildfire forecast is computed using a combination of weather, satellite, and fire history features:
        <ul>
            <li>3-day weather forecasts (temperature, precipitation, wind)</li>
            <li>MODIS satellite features (NDVI, EVI, LST)</li>
            <li>Fire activity in the past 7 days around the city</li>
        </ul>
        </p>

        <p style="font-size:14px;">
        <strong>Probability (PROB)</strong>: The model outputs a value between 0 and 1 representing the likelihood of a wildfire.<br>
        <em>PROB_PERCENT = PROB × 100</em> → e.g., PROB = 0.25 → 25% chance of wildfire.
        </p>

        <p style="font-size:14px;">
        <strong>Confidence (CONFIDENCE)</strong>: Measures how extreme the prediction is, computed as:<br>
        <em>CONFIDENCE = 1 - |0.5 - PROB| × 2</em><br>
        <em>CONF_PERCENT = CONFIDENCE × 100</em><br>
        Higher confidence near very low (<25%) or very high (>75%) probabilities, lower near 50%.
        </p>

        <p style="font-size:14px;">
        <strong>Interpretation:</strong><br>
        <ul>
            <li>Probability 0–25% → Low chance of wildfire</li>
            <li>Probability 25–50% → Moderate chance</li>
            <li>Probability >50% → High chance</li>
            <li>Confidence 0–50% → Model is uncertain</li>
            <li>Confidence 50–100% → Model is more sure about the prediction</li>
        </ul>
        </p>

        <p style="font-size:14px;">
        These predictions are <strong>approximations</strong> and should not be used as guarantees.
        </p>
        """,
        unsafe_allow_html=True
    )


# -------------------------
# Cities to predict
# -------------------------
CITIES = {
    "Los Angeles": (34.05, -118.25),
    "San Francisco": (37.77, -122.42)
}



# Create a container for side-by-side city forecasts
city_cols = st.columns(len(CITIES))

for idx, (city, (LAT, LON)) in enumerate(CITIES.items()):
    with city_cols[idx]:
        st.header(city)

        # -------------------------
        # Static environmental data
        # -------------------------
        modis = fetch_modis(LAT, LON)
        fire_last_7 = fetch_fire_last_7(LAT, LON, city_name=city)

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
            confidence = abs(prob - 0.5) * 2


            predictions.append({
                "DATE": latest["DATE"],
                "PROB": prob,
                "CONFIDENCE": confidence
            })

        forecast_df = pd.DataFrame(predictions)
        forecast_df["PROB_PERCENT"] = (forecast_df["PROB"] * 100).round(1)
        forecast_df["CONF_PERCENT"] = (forecast_df["CONFIDENCE"] * 100).round(0)

        # -------------------------
        # Display colored cards for probability/confidence
        # -------------------------
        for idx2, row in forecast_df.iterrows():
            prob = row["PROB"]
            conf = row["CONFIDENCE"]
            prob_pct = row["PROB_PERCENT"]
            conf_pct = row["CONF_PERCENT"]

            # Color-coded risk card
            if prob < 0.25:
                risk_color = "#16af16"  # Green
                risk_text = "Low"
            elif prob < 0.5:
                risk_color = "#f7b017"  # Yellow/Orange
                risk_text = "Moderate"
            else:
                risk_color = "#f11818"  # Red
                risk_text = "High"

            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, {risk_color}33, {risk_color}99); /* soft gradient */
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    margin-bottom: 15px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15); /* subtle shadow */
                    transition: transform 0.2s;
                ">
                    <h3 style="margin-bottom:5px; font-size:26px;">{row['DATE']}</h3>
                    <p style="font-size:24px; margin:2px 0; font-weight:bold;"> Probability: {prob_pct}%</p>
                    <span style="margin:2px 0; font-size:16px; padding:2px 8px;border-radius:12px;border: 1.5px solid #555;"> Confidence: {conf_pct}%</span>
                    <p style="margin-top:8px; font-size:18px; font-weight:600;"> Risk Level: {risk_text}</p>
                </div>

                """,
                unsafe_allow_html=True
            )

        # -------------------------
        # 3-day Probability Trend Chart
        # -------------------------
        fig = px.line(
            forecast_df, x="DATE", y="PROB_PERCENT",
            title=f"{city} 3-Day Wildfire Probability Trend",
            markers=True,
            labels={"PROB_PERCENT": "Probability (%)", "DATE": "Date"}
        )
        st.plotly_chart(fig, use_container_width=True)

        # -------------------------
        # Raw Features (always expanded)
        # -------------------------
        st.subheader(f"{city} Latest Environmental Features")

        # Convert the dict to a dataframe for a clean tabular display
        latest_df = pd.DataFrame(list(latest.to_dict().items()), columns=["Feature", "Value"])
        latest_df["Value"] = latest_df["Value"].apply(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)
        st.table(latest_df)


        # -------------------------
        # Historical CSV Table (always expanded)
        # -------------------------
        st.subheader(f"{city} Historical Data (Rolling Features)")
        csv_file = f"data_store/history_{city.replace(' ', '_')}.csv"
        if os.path.exists(csv_file):
            df_hist = pd.read_csv(csv_file)
            st.dataframe(df_hist)
        else:
            st.info("No history data available yet for this city.")
