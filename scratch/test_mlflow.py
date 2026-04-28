import mlflow
import os
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(uri)
print(f"Tracking URI: {mlflow.get_tracking_uri()}")

try:
    mlflow.set_experiment("Test_Experiment")
    with mlflow.start_run():
        mlflow.log_param("test_param", 42)
        mlflow.log_metric("test_metric", 0.95)
    print("Successfully logged to MLflow!")
except Exception as e:
    print(f"Failed to log to MLflow: {e}")
