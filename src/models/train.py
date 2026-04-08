"""Pipeline de treinamento com MLflow tracking padronizado."""
import logging
import mlflow
import pandas as pd
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from typing import Any

logger = logging.getLogger(__name__)

def train_and_log(
    df: pd.DataFrame,
    target_col: str,
    model_name: str,
    model_class: Any,
    model_params: dict[str, Any],
    test_size: float = 0.2,
    random_state: int = 42,
) -> str:
    """Treina modelo, loga tudo no MLflow, retorna run_id."""
    X = df.drop(columns=[target_col])
    y = df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    with mlflow.start_run(run_name=model_name) as run:
        mlflow.log_params(model_params)
        mlflow.log_param("test_size", test_size)
        mlflow.log_param("random_state", random_state)
        mlflow.log_param("n_features", X_train.shape[1])
        mlflow.log_param("n_samples_train", X_train.shape[0])

        mlflow.set_tag("model_type", "classification")
        mlflow.set_tag("framework", model_class.__module__.split(".")[0])
        mlflow.set_tag("owner", "grupo-XX")
        mlflow.set_tag("phase", "datathon-fase05")

        model = model_class(**model_params)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        metrics = {
            "auc": roc_auc_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
        }
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, "model")

        logger.info(
            "Modelo %s treinado: AUC=%.4f, F1=%.4f",
            model_name,
            metrics["auc"],
            metrics["f1"],
        )
        return str(run.info.run_id)
