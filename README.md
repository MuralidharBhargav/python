## Install Graphviz dependencies:

sudo apt-get install graphviz libgraphviz-dev

## Project Structure - MetaData

/your-project
  |-- gcs_logging_fetcher.py
  |-- dataproc_logging_fetcher.py
  |-- bq_metadata_collector.py
  |-- datacatalog_tagging.py
  |-- main_orchestrator.py   # (optional orchestrator to call everything!)


from google.cloud import logging_v2
from datetime import datetime, timedelta
import time

# Initialize Cloud Logging client
client = logging_v2.Client()

# Your parameters
project_id = 'your-project-id'
dataset_name = 'your_dataset'
poll_interval = 30  # seconds

# Build the filter to catch table changes in the dataset
log_filter = f"""
resource.type="bigquery_resource"
protoPayload.serviceData.jobCompletedEvent.job.jobStatistics.referencedTables:("{dataset_name}")
OR protoPayload.resourceName:"{dataset_name}"
protoPayload.methodName=~"(Insert|Load|Update|Delete)"
"""

def poll_logs():
    # Get logs from the last X minutes
    time_window_start = (datetime.utcnow() - timedelta(minutes=5)).isoformat("T") + "Z"
    entries = client.list_entries(
        filter_=log_filter,
        order_by=logging_v2.DESCENDING,
        page_size=20,
        project_ids=[project_id],
    )
    events = []
    for entry in entries:
        payload = entry.payload
        timestamp = entry.timestamp
        method = payload.get('methodName', 'UNKNOWN')
        resource = payload.get('resourceName', 'UNKNOWN')
        principal_email = payload.get('authenticationInfo', {}).get('principalEmail', 'UNKNOWN')
        events.append({
            'timestamp': timestamp,
            'method': method,
            'resource': resource,
            'user': principal_email
        })
    return events

# Poll in loop
while True:
    print(f"\n🔄 Checking logs at {datetime.utcnow().isoformat()}...")
    events = poll_logs()
    if events:
        for event in events:
            print(f"✅ [{event['timestamp']}] {event['method']} on {event['resource']} by {event['user']}")
    else:
        print("No new events.")
    time.sleep(poll_interval)


