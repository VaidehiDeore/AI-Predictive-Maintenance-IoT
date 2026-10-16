# ForgeSense — AI-Powered Predictive Maintenance for IoT Devices

ForgeSense is a software-based predictive maintenance system that uses machine learning and simulated IoT sensor readings to estimate equipment failure risk. It provides an interactive dashboard for monitoring equipment health, analyzing sensor data, viewing maintenance alerts, and exploring predictive maintenance insights.

> **Note:** This project uses simulated sensor data and is intended for educational and demonstration purposes. It is not connected to physical industrial equipment.

## Features

- **Equipment Health Monitoring:** View equipment status and health indicators.
- **Live Simulation:** Generate simulated sensor readings to demonstrate changing machine conditions.
- **Failure Risk Prediction:** Use a trained machine learning model to estimate equipment failure risk.
- **Predictive Analytics:** Visualize sensor trends and model evaluation results.
- **Maintenance Alerts:** Display risk-based warnings to support maintenance planning.
- **Interactive Dashboard:** Navigate between overview, equipment, monitoring, analytics, and alerts.

## Technology Stack

- **Backend:** Python, Flask
- **Machine Learning:** Scikit-learn
- **Data Processing:** Pandas, NumPy
- **Frontend:** HTML, CSS, JavaScript
- **Model Storage:** Joblib
- **Testing:** Pytest

## Project Structure

```text
AI-Predictive-Maintenance-IoT/
├── data/          # Dataset and sample sensor data
├── docs/          # Project documentation
├── images/        # Dashboard screenshots
├── models/        # Trained machine learning model
├── outputs/       # Evaluation results and generated outputs
├── src/           # Data processing and ML modules
├── tests/         # Automated tests
├── web/           # Dashboard HTML, CSS and JavaScript
├── app.py         # Main application and API logic
├── main.py        # Application entry point
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

**Requirements:** Python 3.11 or a compatible version supported by the project's dependencies.

1. Clone the repository:

   ```bash
   git clone <YOUR_GITHUB_REPOSITORY_URL>
   cd AI-Predictive-Maintenance-IoT
   ```

2. Create and activate a virtual environment:

   **Windows PowerShell**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

## Running the Application

Start the dashboard using the Flask application:

```bash
python app.py
```

Open the local URL displayed in the terminal. Use the dashboard navigation to explore equipment, start the live simulation, review analytics, and inspect maintenance alerts.

If the application requires a trained model or dataset, ensure the corresponding project files are present before starting it.

## Testing

Run the automated tests from the project root:

```bash
python -m pytest -q
```

## Results and Limitations

ForgeSense demonstrates an end-to-end predictive maintenance workflow using synthetic data, a trained classification model, simulated sensor monitoring, and a dashboard interface. Model performance depends on the dataset, feature quality, and evaluation methodology. Synthetic-data results do not establish real-world industrial reliability.

The system is a prototype and has not been validated for safety-critical or production industrial environments.

## Future Scope

- Integrate physical IoT sensors and edge devices.
- Evaluate the model on real-world equipment datasets.
- Improve early-failure detection and model generalization.
- Add historical trend analysis and maintenance reporting.
- Explore cloud-based monitoring and alert delivery.

## Learning Outcomes

This project demonstrates practical experience with Python, machine learning workflows, sensor-data simulation, backend development, dashboard design, model evaluation, and automated testing.
