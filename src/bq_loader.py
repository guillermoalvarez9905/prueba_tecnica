import logging

from google.cloud import bigquery

logger = logging.getLogger(__name__)


class BigQueryLoader:
    def __init__(self, project_id: str):
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id

    def create_dataset(self, dataset_id: str, location: str = "EU") -> None:
        dataset_ref = f"{self.project_id}.{dataset_id}"
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        self.client.create_dataset(dataset, exists_ok=True)
        logger.info("Dataset '%s' creado correctamente", dataset_id)

    def load_data(
        self,
        rows: list[dict],
        dataset_id: str,
        table_id: str,
        schema: list[bigquery.SchemaField],
        write_mode: str = "WRITE_TRUNCATE",
    ) -> bigquery.LoadJob:
        table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition=getattr(bigquery.WriteDisposition, write_mode),
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )
        job = self.client.load_table_from_json(rows, table_ref, job_config=job_config)
        job.result()
        table = self.client.get_table(table_ref)
        logger.info("%d filas cargadas en '%s'", table.num_rows, table_ref)
        return job
