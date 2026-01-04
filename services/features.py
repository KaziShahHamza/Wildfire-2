import pandas as pd
import os

STORE_DIR = "data_store"

# Columns that must never exist anymore
DEPRECATED_COLUMNS = [
    "LAGGED_PRECIPITATION",
    "LAGGED_AVG_WIND_SPEED"
]

def get_season(month):
    if month in [12, 1, 2]:
        return 0  # Winter
    elif month in [3, 4, 5]:
        return 1  # Spring
    elif month in [6, 7, 8]:
        return 2  # Summer
    else:
        return 3  # Fall

def update_history(row: dict, city: str):
    """
    Updates/creates rolling features history for a given city
    """
    os.makedirs(STORE_DIR, exist_ok=True)
    store_file = os.path.join(STORE_DIR, f"history_{city.replace(' ', '_')}.csv")

    # Load city history
    if os.path.exists(store_file) and os.path.getsize(store_file) > 0:
        df = pd.read_csv(store_file)
        # Remove deprecated columns
        df.drop(
            columns=[c for c in DEPRECATED_COLUMNS if c in df.columns],
            inplace=True,
            errors="ignore"
        )
    else:
        df = pd.DataFrame()

    # -------------------------
    # Base derived features
    # -------------------------
    row["TEMP_RANGE"] = row["MAX_TEMP"] - row["MIN_TEMP"]
    row["SEASON"] = get_season(row["MONTH"])

    if pd.isna(row.get("LST_C")):
        row["LST_C"] = (row["MAX_TEMP"] + row["MIN_TEMP"]) / 2

    row["dryness"] = (
        (row["MAX_TEMP"] - row["PRECIPITATION"]) /
        (row["PRECIPITATION"] + 1)
    )

    # -------------------------
    # Append & trim to last 7 days
    # -------------------------
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df = df.tail(7)

    # -------------------------
    # Rolling features
    # -------------------------
    df["roll_precip_7"] = df["PRECIPITATION"].rolling(7, min_periods=1).mean()
    df["roll_wind_7"] = df["AVG_WIND_SPEED"].rolling(7, min_periods=1).mean()
    df["roll_temp_range_7"] = df["TEMP_RANGE"].rolling(7, min_periods=1).mean()
    df["roll_ndvi_3"] = df["NDVI"].rolling(3, min_periods=1).mean()
    df["roll_evi_3"] = df["EVI"].rolling(3, min_periods=1).mean()

    # Cleanup
    df.fillna(0, inplace=True)

    df.to_csv(store_file, index=False)
    return df
