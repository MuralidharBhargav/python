# semantic_search.py

from google.cloud import datacatalog_v1

def semantic_search_metadata(query_text, project_id):
    """Perform a semantic free-text search across Data Catalog."""

    # Initialize Data Catalog client
    datacatalog = datacatalog_v1.DataCatalogClient()

    # Define Scope
    scope = datacatalog_v1.types.SearchCatalogRequest.Scope(
        include_project_ids=[project_id]
    )

    # Perform search
    print(f"🔎 Performing semantic search for: '{query_text}'")
    response = datacatalog.search_catalog(
        request={
            "scope": scope,
            "query": query_text,
        }
    )

    results = []
    for result in response:
        metadata = {
            "relative_resource_name": result.relative_resource_name,
            "display_name": result.display_name,
            "linked_resource": result.linked_resource,
            "search_result_type": result.search_result_type.name,
            "search_result_subtype": result.search_result_subtype,
        }
        results.append(metadata)

    return results

if __name__ == "__main__":
    project_id = "gbmamgdataeval"

    # Example 1
    results = semantic_search_metadata("critical sales tables", project_id)
    for res in results:
        print(f"✅ {res['display_name']} ({res['linked_resource']})")

    # Example 2
    results = semantic_search_metadata("dataproc jobs failed yesterday", project_id)
    for res in results:
        print(f"✅ {res['display_name']} ({res['linked_resource']})")
