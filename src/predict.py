"""Prediction helpers shared by the CLI and web API."""
import joblib
import pandas as pd
from src.config import MODEL_PATH, FEATURE_COLUMNS
from src.train import train_model

def load_bundle():
    if not MODEL_PATH.exists():
        train_model()
    return joblib.load(MODEL_PATH)

def predict_one(payload: dict) -> dict:
    bundle = load_bundle()
    missing = [name for name in FEATURE_COLUMNS if name not in payload]
    if missing:
        raise ValueError("Missing required sensor fields: " + ", ".join(missing))
    frame = pd.DataFrame([{name: float(payload[name]) for name in FEATURE_COLUMNS}])
    model = bundle["model"]
    probability = float(model.predict_proba(frame)[0, 1])
    predicted_failure = int(probability >= 0.5)
    if probability >= 0.75:
        risk = "CRITICAL"
        recommendation = "Escalate for immediate inspection; review vibration, temperature, and load."
    elif probability >= 0.5:
        risk = "HIGH"
        recommendation = "Schedule maintenance soon and inspect abnormal sensor readings."
    elif probability >= 0.3:
        risk = "WATCH"
        recommendation = "Continue monitoring and review the next maintenance window."
    else:
        risk = "NORMAL"
        recommendation = "Machine appears stable; continue routine monitoring."
    return {
        "predicted_failure": predicted_failure,
        "prediction": "FAILURE RISK" if predicted_failure else "NO FAILURE FLAG",
        "failure_probability": round(probability, 4),
        "risk_level": risk,
        "recommendation": recommendation,
    }
