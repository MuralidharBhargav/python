# main_orchestrator.py

from gcs_logging_fetcher import fetch_gcs_uploads
from dataproc_logging_fetcher import fetch_dataproc_jobs
from bq_metadata_collector import collect_bq_table_metadata
from datacatalog_tagging import attach_tags

from datetime import datetime

# Configurations
PROJECT_ID = "gbmamgdataeval"
LOCATION = "europe-west2"

# --- User input ---
FILE_PATTERN = "gs://amgdatabucket/sales-data-*.csv"

def orchestrate_metadata_collection(file_pattern):
    print(f"🔍 Starting Metadata Collection for file pattern: {file_pattern}")

    # 1. Fetch GCS Upload Events
    gcs_files = fetch_gcs_uploads(file_pattern, PROJECT_ID)
    print(f"✅ Found {len(gcs_files)} matching GCS files.")

    # 2. Fetch Dataproc Jobs Processing Those Files
    dataproc_jobs = fetch_dataproc_jobs(file_pattern, PROJECT_ID)
    print(f"✅ Found {len(dataproc_jobs)} matching Dataproc jobs.")

    if not dataproc_jobs:
        print("⚠️ No Dataproc jobs found matching the file pattern!")
        return

    # 3. For each Dataproc Job
    for job in dataproc_jobs:
        print(f"🔎 Processing Dataproc Job ID: {job['job_id']}")

        # (Optional enhancement: match which output tables belong to which file)
        output_tables = job.get("output_tables", [])
        
        if not output_tables:
            print(f"⚠️ No output tables linked to job {job['job_id']}. Skipping tagging.")
            continue

        # 4. For each output table
        for table_id in output_tables:
            # Expecting format: project.dataset.table
            project_id, dataset_id, table_name = table_id.split('.')

            # Fetch Technical Metadata
            bq_metadata = collect_bq_table_metadata(project_id, dataset_id, table_name)

            # Build Operational Metadata
            operational_metadata = {
                "source_file": gcs_files[0]['bucket'] + "/" + gcs_files[0]['object'] if gcs_files else "unknown",
                "job_id": job["job_id"],
                "job_status": job["status"],  # You might extend to detect true job status from job logs
                "start_time": datetime.now(),
                "end_time": datetime.now(),
                "freshness_status": "FRESH",
            }

            # Build Technical Metadata
            technical_metadata = {
                "owner": "data.owner@example.com",
                "last_modified": bq_metadata.get("last_modified"),
                "last_queried": bq_metadata.get("last_modified"),  # Simplification
                "num_rows": bq_metadata.get("num_rows"),
                "size_bytes": bq_metadata.get("size_bytes"),
                "table_type": bq_metadata.get("table_type"),
            }

            # Build Business Metadata
            business_metadata = {
                "business_owner": "sales@company.com",
                "criticality": "HIGH",
                "sla_hours": 24,
                "business_process": "Sales Reporting",
            }

            # 5. Attach Tags
            print(f"🏷️ Attaching tags to {table_id}...")
            attach_tags(
                entry_name=bq_metadata.get("entry_resource_name"),
                project_id=PROJECT_ID,
                location=LOCATION,
                operational_data=operational_metadata,
                technical_data=technical_metadata,
                business_data=business_metadata
            )

if __name__ == "__main__":
    orchestrate_metadata_collection(FILE_PATTERN)
