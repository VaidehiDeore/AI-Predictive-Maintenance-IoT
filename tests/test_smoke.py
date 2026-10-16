from src.data_generator import generate_dataset
from src.config import FEATURE_COLUMNS
from src.predict import predict_one

def test_dataset_shape_and_columns(tmp_path):
    path = tmp_path / "sample.csv"
    df = generate_dataset(rows=120, output_path=path)
    assert len(df) == 120
    assert set(FEATURE_COLUMNS).issubset(df.columns)
    assert "failure" in df.columns

def test_prediction_returns_risk_fields():
    result = predict_one({
        "temperature_c": 70, "vibration_mm_s": 3.5, "current_a": 9,
        "pressure_bar": 6, "rpm": 1350, "machine_age_years": 7,
        "hours_since_maintenance": 300
    })
    assert result["risk_level"] in {"NORMAL", "WATCH", "HIGH", "CRITICAL"}
    assert 0 <= result["failure_probability"] <= 1
