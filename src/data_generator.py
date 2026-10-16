"""Generate clearly labelled synthetic IoT sensor records for a software-only demo."""
from pathlib import Path
import numpy as np
import pandas as pd
from src.config import DATASET_PATH, RANDOM_STATE

def generate_dataset(rows: int = 3500, output_path: Path = DATASET_PATH) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_STATE)
    machine_age = rng.uniform(0.1, 18, rows)
    hours_since_service = rng.gamma(shape=2.2, scale=115, size=rows).clip(0, 1200)
    ambient = rng.normal(24, 4, rows)
    temperature = (ambient + 28 + machine_age * 0.42
                   + hours_since_service * 0.012 + rng.normal(0, 5, rows)).clip(25, 115)
    vibration = (0.7 + machine_age * 0.085 + hours_since_service * 0.0018
                 + rng.lognormal(mean=-0.25, sigma=0.48, size=rows)).clip(0.1, 14)
    current = (4.5 + temperature * 0.055 + vibration * 0.34
               + rng.normal(0, 1.35, rows)).clip(1, 22)
    pressure = (7.2 - vibration * 0.12 - hours_since_service * 0.0007
                + rng.normal(0, 0.55, rows)).clip(1.2, 9.5)
    rpm = (1500 - vibration * 18 - temperature * 1.4
           + rng.normal(0, 85, rows)).clip(450, 1800)

    # Synthetic risk score: deliberately noisy so the learning task is not perfectly separable.
    score = (
        0.035 * (temperature - 65)
        + 0.42 * (vibration - 3.0)
        + 0.10 * (current - 8.0)
        + 0.32 * (5.5 - pressure)
        + 0.002 * (1500 - rpm)
        + 0.035 * (machine_age - 5)
        + 0.0018 * (hours_since_service - 250)
        + rng.normal(0, 1.15, rows)
    )
    probability = 1 / (1 + np.exp(-np.clip(score - 1.3, -10, 10)))
    failure = rng.binomial(1, probability)

    df = pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=rows, freq="15min"),
        "machine_id": rng.choice(["MTR-001", "PMP-002", "CMP-003", "FAN-004"], rows),
        "temperature_c": temperature.round(2),
        "vibration_mm_s": vibration.round(3),
        "current_a": current.round(2),
        "pressure_bar": pressure.round(2),
        "rpm": rpm.round(0).astype(int),
        "machine_age_years": machine_age.round(2),
        "hours_since_maintenance": hours_since_service.round(1),
        "failure": failure,
    })
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df

if __name__ == "__main__":
    frame = generate_dataset()
    print(f"Generated {len(frame):,} synthetic sensor records -> {DATASET_PATH}")
    print(frame.head(5).to_string(index=False))
    print("\nFailure label distribution:")
    print(frame["failure"].value_counts().rename(index={0: "NO_FAILURE", 1: "FAILURE"}))
