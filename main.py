import logging

from google.cloud import bigquery

from src.api_client import APIExtractor
from src.bq_loader import BigQueryLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

PROJECT_ID = "prueba-tecnica-500721"
DATASET_ID = "SANDBOX_FOOTBALL_PLAYERS"
TABLE_ID = "players"

SCHEMA = [
    bigquery.SchemaField("id_player", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("str_player", "STRING"),
    bigquery.SchemaField("str_nationality", "STRING"),
    bigquery.SchemaField("str_team", "STRING"),
    bigquery.SchemaField("str_position", "STRING"),
    bigquery.SchemaField("date_born", "STRING"),
    bigquery.SchemaField("str_sport", "STRING"),
    bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP"),
]


def main():
    extractor = APIExtractor()
    players = extractor.fetch_players()

    loader = BigQueryLoader(project_id=PROJECT_ID)
    loader.create_dataset(DATASET_ID)
    loader.load_data(players, DATASET_ID, TABLE_ID, SCHEMA)


if __name__ == "__main__":
    main()
