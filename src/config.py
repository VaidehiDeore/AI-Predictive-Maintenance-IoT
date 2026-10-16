from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
MODEL_DIR = ROOT_DIR / "models"
OUTPUT_DIR = ROOT_DIR / "outputs"
WEB_DIR = ROOT_DIR / "web"

DATASET_PATH = DATA_DIR / "iot_sensor_data.csv"
MODEL_PATH = MODEL_DIR / "predictive_maintenance_model.joblib"
METRICS_PATH = OUTPUT_DIR / "evaluation_metrics.json"
PREDICTIONS_PATH = OUTPUT_DIR / "test_predictions.csv"

FEATURE_COLUMNS = [
    "temperature_c",
    "vibration_mm_s",
    "current_a",
    "pressure_bar",
    "rpm",
    "machine_age_years",
    "hours_since_maintenance",
]
TARGET_COLUMN = "failure"
RANDOM_STATE = 42
