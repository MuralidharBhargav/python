## Install Graphviz dependencies:

sudo apt-get install graphviz libgraphviz-dev

## Project Structure - MetaData

/your-project
  |-- gcs_logging_fetcher.py
  |-- dataproc_logging_fetcher.py
  |-- bq_metadata_collector.py
  |-- datacatalog_tagging.py
  |-- main_orchestrator.py   # (optional orchestrator to call everything!)
