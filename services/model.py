""" services/model.py"""

import joblib
import pandas as pd

MODEL_PATH = "models/wildfire_model.pkl"
FEATURES_PATH = "models/model_features.pkl"

model = joblib.load(MODEL_PATH)
FEATURES = joblib.load(FEATURES_PATH)

def predict_fire(row: dict):
    X = pd.DataFrame([row])[FEATURES]
    prob = model.predict_proba(X)[0, 1]
    return prob
