import os

# Define folder structure
folders = [
    "config/credentials",
    "metadata_repository/business_metadata/schemas",
    "metadata_repository/business_metadata/rules",
    "metadata_repository/business_metadata/definitions",
    "metadata_repository/technical_metadata/schemas",
    "metadata_repository/technical_metadata/lineage",
    "metadata_repository/technical_metadata/assets",
    "metadata_repository/technical_metadata/tags",
    "metadata_repository/operational_metadata/execution_logs",
    "metadata_repository/operational_metadata/audits",
    "metadata_repository/operational_metadata/performance_metrics",
    "metadata_repository/operational_metadata/incidents",
    "data_quality_checks/sanity_checks/predefined_rules",
    "data_quality_checks/sanity_checks/custom_expectations",
    "data_quality_checks/ai_ml_checks/models/anomaly_detection",
    "data_quality_checks/ai_ml_checks/models/prediction",
    "data_quality_checks/ai_ml_checks/scripts",
    "data_quality_checks/ai_ml_checks/outputs/model_artifacts",
    "data_quality_checks/ai_ml_checks/outputs/results",
    "data_quality_checks/validation_engine",
    "remediation_workflow/workflows/dag_definitions",
    "remediation_workflow/workflows/scripts",
    "remediation_workflow/orchestration/airflow",
    "remediation_workflow/orchestration/cloud_composer",
    "remediation_workflow/notifications",
    "streamlit_app/pages",
    "streamlit_app/components",
    "streamlit_app/data/cached",
    "streamlit_app/assets/images",
    "scripts",
    "tests/unit_tests",
    "tests/integration_tests",
    "tests/test_data",
]

# Files to be created
files = [
    "README.md",
    "requirements.txt",
    "setup.py",
    ".gitignore",
    "config/config.yaml",
    "config/logging.conf",
    "scripts/deploy_streamlit.sh",
    "scripts/init_db.sh",
    "scripts/setup_env.sh",
    "streamlit_app/app.py",
    "data_quality_checks/sanity_checks/predefined_rules/rules.yaml",
    "data_quality_checks/sanity_checks/custom_expectations/expectations.py",
    "data_quality_checks/validation_engine/validator.py",
    "data_quality_checks/validation_engine/report_generator.py",
    "remediation_workflow/notifications/email_alerts.py",
    "remediation_workflow/notifications/teams_notifications.py",
]


def create_structure(base_path="dq-application"):
    for folder in folders:
        path = os.path.join(base_path, folder)
        os.makedirs(path, exist_ok=True)
        print(f"Created folder: {path}")

    for file in files:
        path = os.path.join(base_path, file)
        with open(path, 'w') as f:
            pass  # Creates empty file
        print(f"Created file: {path}")


if __name__ == "__main__":
    create_structure()
