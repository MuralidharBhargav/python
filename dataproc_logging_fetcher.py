# dataproc_logging_fetcher.py

from google.cloud import logging_v2

def fetch_dataproc_jobs(file_pattern, project_id):
    """Fetch Dataproc job logs that processed given GCS file pattern."""
    logging_client = logging_v2.Client(project=project_id)

    filter_str = (
        'resource.type="cloud_dataproc_cluster" '
        'protoPayload.methodName="google.cloud.dataproc.v1.JobController.SubmitJob"'
    )

    entries = logging_client.list_entries(filter_=filter_str)
    
    matching_jobs = []

    for entry in entries:
        payload_str = str(entry)
        if file_pattern in payload_str:
            job_id = entry.proto_payload.response.get("reference", {}).get("jobId")
            cluster_name = entry.resource.labels.get("cluster_name")
            start_time = entry.timestamp

            matching_jobs.append({
                "job_id": job_id,
                "cluster_name": cluster_name,
                "start_time": start_time,
                "status": "UNKNOWN",
                "output_tables": []  # Optionally populate if available from job logs
            })

    return matching_jobs
