from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'ana_auditora',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ana_ml_pipeline',
    default_args=default_args,
    description='Pipeline de MLOps da Ana Auditora (Orquestração DVC)',
    schedule_interval='@daily',
    catchup=False,
    tags=['ml', 'ana', 'dvc'],
) as dag:

    # Comando base para rodar o DVC dentro do contêiner do Airflow
    base_cmd = "cd /app && PYTHONPATH=. "

    task_prepare_data = BashOperator(
        task_id='prepare_data',
        bash_command=f"{base_cmd} dvc repro prepare_data",
    )

    task_train = BashOperator(
        task_id='train_model',
        bash_command=f"{base_cmd} dvc repro train",
    )

    task_inference = BashOperator(
        task_id='inference',
        bash_command=f"{base_cmd} dvc repro inference",
    )

    task_drift = BashOperator(
        task_id='drift_analysis',
        bash_command=f"{base_cmd} dvc repro drift",
    )

    # Fluxo de dependências: Prepare -> Train -> Inference -> Drift
    task_prepare_data >> task_train >> task_inference >> task_drift
