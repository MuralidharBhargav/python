## Install Graphviz dependencies:

sudo apt-get install graphviz libgraphviz-dev

## Project Structure - MetaData

/your-project
  |-- gcs_logging_fetcher.py
  |-- dataproc_logging_fetcher.py
  |-- bq_metadata_collector.py
  |-- datacatalog_tagging.py
  |-- main_orchestrator.py   # (optional orchestrator to call everything!)


from google.cloud import bigquery
from datetime import datetime, timedelta

# === CONFIG ===
project_id = 'your-project-id'
dataset_name = 'your_dataset'
table_name = 'your_table'
region = 'us'  # Example: 'us', 'europe-west2', 'asia-northeast1'
lookback_hours = 24  # How far back to look

# Build the region-based INFORMATION_SCHEMA path
info_schema = f"region-{region}.INFORMATION_SCHEMA.JOBS_BY_PROJECT"

# Time window
time_threshold = (datetime.utcnow() - timedelta(hours=lookback_hours)).isoformat()

# Build the query
query = f"""
SELECT
  creation_time,
  user_email,
  statement_type,
  query
FROM
  `{info_schema}`
WHERE
  creation_time >= TIMESTAMP('{time_threshold}')
  AND statement_type IN ('INSERT', 'UPDATE', 'DELETE')
  AND query LIKE '%{dataset_name}.{table_name}%'
ORDER BY
  creation_time DESC
"""

# Initialize BigQuery client
client = bigquery.Client(project=project_id)

# Run the query
print(f"🔍 Checking recent jobs for {dataset_name}.{table_name} (last {lookback_hours} hours)...\n")

query_job = client.query(query)

# Fetch and display results
results = query_job.result()

found = False
for row in results:
    found = True
    print(f"🕒 {row.creation_time} | 👤 {row.user_email} | 📝 {row.statement_type}")
    print(f"SQL: {row.query[:200]}...")  # Show first 200 chars
    print("-" * 60)

if not found:
    print("✅ No recent INSERT/UPDATE/DELETE jobs found.")

