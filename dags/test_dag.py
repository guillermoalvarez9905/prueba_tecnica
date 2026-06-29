"""
¿Qué es un Hook? ¿En qué se diferencia de una Conexión?

Conexión: almacena los datos de acceso a un sistema externo (una base de datos como
PostgreSQL o MySQL, un servicio cloud como BigQuery o S3, una API, etc.).
Guarda parámetros como host, puerto, usuario, contraseña o proyecto de GCP.
Solo almacena credenciales, no ejecuta ninguna lógica.

Hook: clase Python que recoge esas credenciales y las usa para conectarse y operar
con el sistema externo: ejecutar una query, subir un fichero, leer una tabla, etc.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import BaseOperator
from airflow.operators.dummy import DummyOperator

N = 6

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(1900, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(seconds=5),
}


class TimeDiffOperator(BaseOperator):
    def __init__(self, diff_date: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.diff_date = diff_date

    def execute(self, context):
        target = datetime.strptime(self.diff_date, "%Y-%m-%d")
        diff = datetime.utcnow() - target
        self.log.info("Diferencia entre hoy y %s: %d días", self.diff_date, diff.days)
        return diff.days


with DAG(
    dag_id="test",
    default_args=default_args,
    schedule_interval="0 3 * * *",
    catchup=False,
    description="DAG con operador personalizado que recibe una fecha y muestra la diferencia con la actual",
) as dag:

    start = DummyOperator(task_id="start")
    end = DummyOperator(task_id="end")

    tasks = [DummyOperator(task_id=f"task_{i}") for i in range(1, N + 1)]

    tareas_impares = [tasks[i] for i in range(0, N, 2)]
    tareas_pares = [tasks[i] for i in range(1, N, 2)]

    for odd in tareas_impares:
        for even in tareas_pares:
            odd >> even

    time_diff = TimeDiffOperator(
        task_id="time_diff",
        diff_date="2020-01-01",
    )

    start >> [*tareas_impares]
    for even in tareas_pares:
        even >> time_diff
    time_diff >> end
