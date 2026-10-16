"""Flask API and local web dashboard for the predictive-maintenance demo."""
from datetime import datetime, timezone
from pathlib import Path
import json
import random
import threading
import time
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from src.config import WEB_DIR, DATASET_PATH, METRICS_PATH, FEATURE_COLUMNS
from src.data_generator import generate_dataset
from src.predict import predict_one
from src.train import train_model

app = Flask(__name__, static_folder=None)
CORS(app)
_state_lock = threading.Lock()
_history = []
_simulation_running = False
_simulation_thread = None

def ensure_artifacts():
    if not DATASET_PATH.exists():
        generate_dataset()
    if not METRICS_PATH.exists():
        train_model()

def simulated_reading(index=None):
    """Generate plausible, clearly simulated sensor readings."""
    rng = np.random.default_rng(index)
    temperature = float(np.clip(rng.normal(59, 11), 30, 105))
    vibration = float(np.clip(rng.lognormal(np.log(2.2), 0.48), 0.3, 11))
    current = float(np.clip(rng.normal(8.1 + (temperature-55)*0.035, 1.5), 2, 18))
    pressure = float(np.clip(rng.normal(6.6 - vibration*0.08, 0.6), 2, 9))
    rpm = float(np.clip(rng.normal(1430 - vibration*11, 80), 600, 1750))
    age = float(rng.uniform(1, 14))
    hours = float(rng.uniform(10, 900))
    return {
        "temperature_c": round(temperature, 2),
        "vibration_mm_s": round(vibration, 3),
        "current_a": round(current, 2),
        "pressure_bar": round(pressure, 2),
        "rpm": round(rpm),
        "machine_age_years": round(age, 2),
        "hours_since_maintenance": round(hours, 1),
    }

def make_record(reading):
    result = predict_one(reading)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "machine_id": random.choice(["MTR-001", "PMP-002", "CMP-003", "FAN-004"]),
        **reading,
        **result,
    }
    return record

def simulation_loop():
    global _simulation_running
    while True:
        with _state_lock:
            if not _simulation_running:
                break
        try:
            record = make_record(simulated_reading())
            with _state_lock:
                _history.insert(0, record)
                del _history[100:]
        except Exception as exc:
            print(f"Simulation tick failed: {exc}")
        time.sleep(2.5)

@app.route("/")
def index():
    ensure_artifacts()
    return send_from_directory(WEB_DIR, "index.html")

@app.route("/<path:filename>")
def web_assets(filename):
    return send_from_directory(WEB_DIR, filename)

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "project": "AI Predictive Maintenance", "mode": "synthetic simulation"})

@app.get("/api/overview")
def overview():
    ensure_artifacts()
    with _state_lock:
        history = list(_history)
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    latest = history[0] if history else make_record(simulated_reading(4))
    return jsonify({
        "latest": latest,
        "history": history,
        "metrics": {k: metrics[k] for k in ["accuracy", "precision", "recall", "f1_score", "roc_auc", "dataset_rows", "failure_rate"]},
        "simulation_running": _simulation_running,
        "sample_data": True,
    })

@app.post("/api/predict")
def predict():
    payload = request.get_json(silent=True) or {}
    try:
        result = predict_one(payload)
        return jsonify({"input": payload, **result})
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/api/simulation/start")
def start_simulation():
    global _simulation_running, _simulation_thread
    ensure_artifacts()
    with _state_lock:
        if not _simulation_running:
            _simulation_running = True
            _simulation_thread = threading.Thread(target=simulation_loop, daemon=True)
            _simulation_thread.start()
    return jsonify({"status": "started", "message": "Virtual sensor stream started."})

@app.post("/api/simulation/stop")
def stop_simulation():
    global _simulation_running
    with _state_lock:
        _simulation_running = False
    return jsonify({"status": "stopped", "message": "Virtual sensor stream stopped."})

@app.get("/api/alerts")
def alerts():
    with _state_lock:
        history = list(_history)
    return jsonify([r for r in history if r["risk_level"] in ("HIGH", "CRITICAL")][:20])

if __name__ == "__main__":
    ensure_artifacts()
    app.run(host="127.0.0.1", port=5000, debug=False)
