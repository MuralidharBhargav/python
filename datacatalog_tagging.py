# datacatalog_tagging.py

from google.cloud import datacatalog_v1

datacatalog = datacatalog_v1.DataCatalogClient()

def attach_tags(entry_name, project_id, location, operational_data, technical_data, business_data):
    """Attach operational, technical, and business metadata tags."""

    # Tag Templates
    operational_template = f"projects/{project_id}/locations/{location}/tagTemplates/operational_metadata"
    technical_template = f"projects/{project_id}/locations/{location}/tagTemplates/technical_metadata"
    business_template = f"projects/{project_id}/locations/{location}/tagTemplates/business_metadata"

    # Prepare Operational Tag
    operational_tag = datacatalog_v1.Tag(
        template=operational_template,
        fields={
            "source_file": datacatalog_v1.TagField(string_value=operational_data.get("source_file")),
            "job_id": datacatalog_v1.TagField(string_value=operational_data.get("job_id")),
            "job_status": datacatalog_v1.TagField(enum_value=datacatalog_v1.TagField.EnumValue(display_name=operational_data.get("job_status"))),
            "start_time": datacatalog_v1.TagField(timestamp_value=operational_data.get("start_time")),
            "end_time": datacatalog_v1.TagField(timestamp_value=operational_data.get("end_time")),
            "freshness_status": datacatalog_v1.TagField(enum_value=datacatalog_v1.TagField.EnumValue(display_name=operational_data.get("freshness_status"))),
        }
    )

    # Prepare Technical Tag
    technical_tag = datacatalog_v1.Tag(
        template=technical_template,
        fields={
            "owner": datacatalog_v1.TagField(string_value=technical_data.get("owner")),
            "last_modified_time": datacatalog_v1.TagField(timestamp_value=technical_data.get("last_modified")),
            "last_queried_time": datacatalog_v1.TagField(timestamp_value=technical_data.get("last_queried")),
            "num_rows": datacatalog_v1.TagField(double_value=technical_data.get("num_rows")),
            "size_bytes": datacatalog_v1.TagField(double_value=technical_data.get("size_bytes")),
            "table_type": datacatalog_v1.TagField(enum_value=datacatalog_v1.TagField.EnumValue(display_name=technical_data.get("table_type"))),
        }
    )

    # Prepare Business Tag
    business_tag = datacatalog_v1.Tag(
        template=business_template,
        fields={
            "business_owner": datacatalog_v1.TagField(string_value=business_data.get("business_owner")),
            "criticality": datacatalog_v1.TagField(enum_value=datacatalog_v1.TagField.EnumValue(display_name=business_data.get("criticality"))),
            "sla_hours": datacatalog_v1.TagField(double_value=business_data.get("sla_hours")),
            "business_process": datacatalog_v1.TagField(string_value=business_data.get("business_process")),
        }
    )

    # Attach Tags
    datacatalog.create_tag(parent=entry_name, tag=operational_tag)
    datacatalog.create_tag(parent=entry_name, tag=technical_tag)
    datacatalog.create_tag(parent=entry_name, tag=business_tag)

    print(f"✅ Tags successfully attached to {entry_name}")
