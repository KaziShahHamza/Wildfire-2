"""wildfile.services.features"""
import pandas as pd
import os

STORE = "data_store/history.csv"

def get_season(month):
    if month in [12, 1, 2]:
        return 0
    elif month in [3, 4, 5]:
        return 1
    elif month in [6, 7, 8]:
        return 2
    else:
        return 3

def update_history(row):
    os.makedirs(os.path.dirname(STORE), exist_ok=True)

    if os.path.exists(STORE) and os.path.getsize(STORE) > 0:
        df = pd.read_csv(STORE)
    else:
        df = pd.DataFrame()

    # Base derived features
    row["TEMP_RANGE"] = row["MAX_TEMP"] - row["MIN_TEMP"]
    row["SEASON"] = get_season(row["MONTH"])

    if pd.isna(row["LST_C"]):
        row["LST_C"] = (row["MAX_TEMP"] + row["MIN_TEMP"]) / 2

    row["dryness"] = (row["MAX_TEMP"] - row["PRECIPITATION"]) / (row["PRECIPITATION"] + 1)

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df = df.tail(7)

    # Lagged features (yesterday)
    df["LAGGED_PRECIPITATION"] = df["PRECIPITATION"].shift(1)
    df["LAGGED_AVG_WIND_SPEED"] = df["AVG_WIND_SPEED"].shift(1)

    # Rolling features
    df["roll_precip_7"] = df["PRECIPITATION"].rolling(7, min_periods=1).mean()
    df["roll_wind_7"] = df["AVG_WIND_SPEED"].rolling(7, min_periods=1).mean()
    df["roll_temp_range_7"] = df["TEMP_RANGE"].rolling(7, min_periods=1).mean()
    df["roll_ndvi_3"] = df["NDVI"].rolling(3, min_periods=1).mean()
    df["roll_evi_3"] = df["EVI"].rolling(3, min_periods=1).mean()

    # Fill first-day lag NaNs safely
    df.fillna(0, inplace=True)

    df.to_csv(STORE, index=False)
    return df
