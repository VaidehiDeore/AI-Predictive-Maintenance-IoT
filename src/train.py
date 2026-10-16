"""Train and evaluate a baseline failure classifier."""
import json
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from src.config import (
    DATASET_PATH, MODEL_PATH, METRICS_PATH, PREDICTIONS_PATH,
    FEATURE_COLUMNS, TARGET_COLUMN, RANDOM_STATE
)
from src.data_generator import generate_dataset

def train_model():
    if not DATASET_PATH.exists():
        generate_dataset()
    df = pd.read_csv(DATASET_PATH)
    df = df.dropna(subset=[TARGET_COLUMN]).copy()
    X, y = df[FEATURE_COLUMNS], df[TARGET_COLUMN].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("classifier", RandomForestClassifier(
            n_estimators=220, max_depth=12, min_samples_leaf=3,
            class_weight="balanced_subsample", random_state=RANDOM_STATE, n_jobs=-1
        )),
    ])
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    metrics = {
        "dataset_rows": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "failure_rate": round(float(y.mean()), 4),
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, predictions, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
        "classification_report": classification_report(
            y_test, predictions, target_names=["No failure", "Failure"], output_dict=True,
            zero_division=0
        ),
        "model": "RandomForestClassifier",
        "dataset_note": "Synthetic educational data; metrics are not evidence of real-world industrial performance."
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURE_COLUMNS}, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    out = X_test.copy()
    out["actual_failure"] = y_test.to_numpy()
    out["predicted_failure"] = predictions
    out["failure_probability"] = probabilities.round(4)
    out.to_csv(PREDICTIONS_PATH, index=False)
    print("Training complete.")
    print(f"Rows: {len(df)} | Train: {len(X_train)} | Test: {len(X_test)}")
    print(f"Accuracy: {metrics['accuracy']:.3f} | Precision: {metrics['precision']:.3f} | "
          f"Recall: {metrics['recall']:.3f} | F1: {metrics['f1_score']:.3f} | "
          f"ROC-AUC: {metrics['roc_auc']:.3f}")
    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved metrics: {METRICS_PATH}")
    return metrics

if __name__ == "__main__":
    train_model()
