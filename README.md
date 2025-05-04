## Install Graphviz dependencies:

sudo apt-get install graphviz libgraphviz-dev

## Project Structure - MetaData

/your-project
  |-- gcs_logging_fetcher.py
  |-- dataproc_logging_fetcher.py
  |-- bq_metadata_collector.py
  |-- datacatalog_tagging.py
  |-- main_orchestrator.py   # (optional orchestrator to call everything!)


import pandas as pd
import great_expectations as gx
from google.oauth2 import service_account
from google.cloud import bigquery

# ---- CONFIGURATION ----
project_id = 'your-project-id'
dataset_id = 'your_dataset'
table_id = 'your_table'
bq_results_table = 'your_dataset.validation_results'
service_account_file = 'path/to/service_account.json'  # optional

# ---- LOAD BIGQUERY TABLE INTO PANDAS ----
credentials = service_account.Credentials.from_service_account_file(service_account_file)
query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_id}`"
df = pd.read_gbq(query, project_id=project_id, credentials=credentials)

# ---- INITIALIZE GX CONTEXT ----
context = gx.get_context()

# ---- CREATE EXPECTATION SUITE ----
suite_name = "auto_profiled_suite"
context.create_expectation_suite(suite_name, overwrite_existing=True)

# ---- ADD DATASOURCE + DATAFRAME ASSET ----
datasource = context.sources.add_pandas(name="my_pandas")
df_asset = datasource.add_dataframe_asset(name="my_asset", dataframe=df)
batch_request = df_asset.build_batch_request()

# ---- VALIDATOR + PROFILE ----
validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name=suite_name
)
validator.profile()
context.save_expectation_suite(validator.expectation_suite)

# ---- CREATE AND RUN CHECKPOINT ----
checkpoint = context.add_or_update_checkpoint(
    name="my_checkpoint",
    validator=validator,
)
checkpoint_result = checkpoint.run()

# ---- PROCESS RESULTS ----
validation_summary = []
for result in checkpoint_result.list_validation_results():
    for evr in result['results']:
        validation_summary.append({
            'expectation_type': evr['expectation_config']['expectation_type'],
            'column': evr['expectation_config'].get('kwargs', {}).get('column', ''),
            'success': evr['success'],
            'observed_value': str(evr.get('result', {}).get('observed_value', '')),
        })

summary_df = pd.DataFrame(validation_summary)

# ---- LOG TO BIGQUERY ----
bq_client = bigquery.Client(credentials=credentials, project=project_id)

job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
)
table_ref = f"{project_id}.{bq_results_table}"

job = bq_client.load_table_from_dataframe(summary_df, table_ref, job_config=job_config)
job.result()

print(f"Validation results written to BigQuery table: {table_ref}")
