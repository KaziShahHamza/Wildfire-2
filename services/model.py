""" services/model.py """

import joblib
import pandas as pd

MODEL_PATH = "models/xgboost_wildfire_app.pkl"

# Load bundled model + feature schema
bundle = joblib.load(MODEL_PATH)

model = bundle["model"]
FEATURES = bundle["features"]

def predict_fire(row: dict):
    """
    Returns wildfire probability (0–1)
    """
    X = pd.DataFrame([row])[FEATURES]
    prob = model.predict_proba(X)[0, 1]
    return prob
