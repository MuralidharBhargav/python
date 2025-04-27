# gcs_logging_fetcher.py

from google.cloud import logging_v2

def fetch_gcs_uploads(file_pattern, project_id):
    """Fetch GCS file creation logs matching file pattern."""
    logging_client = logging_v2.Client(project=project_id)

    filter_str = (
        'resource.type="gcs_bucket" '
        'protoPayload.methodName="storage.objects.create"'
    )

    entries = logging_client.list_entries(filter_=filter_str)
    
    matching_files = []

    for entry in entries:
        payload_str = str(entry)
        if file_pattern in payload_str:
            bucket_name = entry.resource.labels.get("bucket_name")
            object_name = entry.proto_payload.resource_name.split("/")[-1]
            timestamp = entry.timestamp
            matching_files.append({
                "bucket": bucket_name,
                "object": object_name,
                "created_at": timestamp
            })

    return matching_files
