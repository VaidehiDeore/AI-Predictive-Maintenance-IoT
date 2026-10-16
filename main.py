"""Convenience entry point: train if needed, generate charts, and launch dashboard."""
from src.train import train_model
from src.visualize import create_charts
from app import app, ensure_artifacts

if __name__ == "__main__":
    ensure_artifacts()
    create_charts()
    print("\nDashboard available at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
