"""Create static charts from evaluation and prediction outputs."""
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.config import DATASET_PATH, METRICS_PATH, PREDICTIONS_PATH, OUTPUT_DIR
from src.data_generator import generate_dataset

def create_charts():
    if not DATASET_PATH.exists():
        generate_dataset()
    df = pd.read_csv(DATASET_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 4))
    df["failure"].value_counts().sort_index().rename(index={0:"No failure",1:"Failure"}).plot(
        kind="bar", ax=ax
    )
    ax.set_title("Synthetic Dataset: Failure Label Distribution")
    ax.set_ylabel("Records")
    ax.set_xlabel("Label")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "failure_distribution.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    df.groupby(pd.to_datetime(df["timestamp"]).dt.date)["temperature_c"].mean().head(40).plot(ax=ax)
    ax.set_title("Average Temperature Over Sample Period")
    ax.set_ylabel("Temperature (°C)")
    ax.set_xlabel("Sample date")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "temperature_trend.png", dpi=160)
    plt.close(fig)

    if METRICS_PATH.exists():
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        matrix = metrics["confusion_matrix"]
        fig, ax = plt.subplots(figsize=(5, 4))
        image = ax.imshow(matrix, cmap="YlOrBr")
        ax.set_xticks([0,1], labels=["No failure", "Failure"])
        ax.set_yticks([0,1], labels=["No failure", "Failure"])
        ax.set_xlabel("Predicted label")
        ax.set_ylabel("Actual label")
        ax.set_title("Confusion Matrix")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(matrix[i][j]), ha="center", va="center")
        fig.colorbar(image, ax=ax)
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "confusion_matrix.png", dpi=160)
        plt.close(fig)

    if PREDICTIONS_PATH.exists():
        pred = pd.read_csv(PREDICTIONS_PATH).head(100).reset_index(drop=True)
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(pred.index, pred["failure_probability"], label="Predicted failure probability")
        ax.axhline(0.5, linestyle="--", label="Decision threshold")
        ax.set_ylim(0, 1)
        ax.set_title("Failure Risk Across Test Samples")
        ax.set_xlabel("Test sample")
        ax.set_ylabel("Probability")
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "failure_risk_predictions.png", dpi=160)
        plt.close(fig)
    print(f"Charts saved in {OUTPUT_DIR}")

if __name__ == "__main__":
    create_charts()
