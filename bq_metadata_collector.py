# bq_metadata_collector.py

from google.cloud import bigquery

def collect_bq_table_metadata(project_id, dataset_id, table_id):
    """Collect technical metadata of a BigQuery table."""
    bq_client = bigquery.Client(project=project_id)

    full_table_id = f"{project_id}.{dataset_id}.{table_id}"

    table = bq_client.get_table(full_table_id)

    metadata = {
        "table_id": full_table_id,
        "table_type": table.table_type,
        "num_rows": table.num_rows,
        "size_bytes": table.num_bytes,
        "last_modified": table.modified,
        "schema": [(field.name, field.field_type) for field in table.schema],
        "entry_resource_name": None,  # Optional: find via Data Catalog
    }

    return metadata
