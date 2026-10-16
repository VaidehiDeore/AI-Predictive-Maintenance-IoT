# Testing and verification checklist

1. Install requirements in an isolated virtual environment.
2. Run `python -m src.data_generator` and confirm `data/iot_sensor_data.csv` is created.
3. Run `python -m src.train` and confirm model + metrics + test predictions are written.
4. Run `python -m src.visualize` and confirm PNG charts appear in `outputs/`.
5. Run `python main.py`, open `http://127.0.0.1:5000`, and confirm the dashboard loads.
6. Click Start live simulation; sensor readings should refresh and alerts should update if risk becomes high.
7. Click Generate new prediction and confirm the risk gauge/recommendation updates.
8. Verify `GET /api/health` returns JSON with status `ok`.
9. Verify missing fields in `POST /api/predict` return HTTP 400 with an explanatory error.

All sensor values are simulated. Screenshots should make that limitation clear.
