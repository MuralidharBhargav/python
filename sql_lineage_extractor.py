
import sqlparse
import pandas as pd
import re

# ---- CONFIGURATION ----
mock_schema = {
    "sales_data": ["id", "amount", "region"],
    "users": ["user_id", "name"]
}

# ---- SQL INPUT ----
sql_query = """
WITH sales AS (
    SELECT * FROM sales_data
),
user_info AS (
    SELECT user_id, name FROM users
),
detailed_sales AS (
    SELECT s.id, s.amount, u.name
    FROM (SELECT id, amount FROM sales) s
    JOIN (SELECT name, user_id FROM user_info) u ON s.id = u.user_id
)
SELECT * FROM detailed_sales;
"""

# ---- LINEAGE EXTRACTION ----
def extract_ctes(sql):
    cte_pattern = re.compile(r"(\w+)\s+AS\s*\((.*?)\)(?=,|\s*WITH|\s*SELECT|\Z)", re.DOTALL | re.IGNORECASE)
    return dict(cte_pattern.findall(sql))

def extract_columns_from_select(select_sql):
    select_sql = select_sql.strip()
    select_clause = re.search(r"SELECT\s+(.*?)\s+FROM", select_sql, re.IGNORECASE | re.DOTALL)
    if not select_clause:
        return []
    columns_raw = select_clause.group(1).strip()
    if columns_raw == '*':
        table_match = re.search(r"FROM\s+(\w+)", select_sql, re.IGNORECASE)
        if table_match:
            table = table_match.group(1)
            return [(table, col) for col in mock_schema.get(table, [])]
        return []
    columns = [col.strip() for col in columns_raw.split(',')]
    results = []
    for col in columns:
        col_parts = col.split('.')
        if len(col_parts) == 2:
            results.append((col_parts[0].strip(), col_parts[1].strip()))
        else:
            results.append(("", col_parts[0].strip()))
    return results

def extract_from_clause(sql):
    match = re.search(r"FROM\s+(.*)", sql, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def map_aliases(sql):
    alias_map = {}
    # This captures patterns like: (SELECT ...) alias
    subquery_pattern = re.findall(r"\(\s*SELECT.*?\)\s+(\w+)", sql, re.DOTALL | re.IGNORECASE)

    for alias in subquery_pattern:
        alias_map[alias] = alias  # Map alias to itself as a sub-table
    return alias_map


def resolve_column_sources(columns, alias_map, destination_table):
    lineage = []
    for col_entry in columns:
        if len(col_entry) == 2:
            alias, column = col_entry
        else:
            alias, column = "", col_entry[0]
        source_table = alias_map.get(alias, alias)
        lineage.append({
            "source_table": source_table,
            "source_column": column,
            "destination_table": destination_table,
            "destination_column": column
        })
    return lineage

# ---- PROCESS ----
cte_map = extract_ctes(sql_query)
alias_map = map_aliases(sql_query)
lineage = []

# Process CTEs
for cte_name, cte_sql in cte_map.items():
    cols = extract_columns_from_select(cte_sql)
    base_table_match = re.search(r"FROM\s+(\w+)", cte_sql, re.IGNORECASE)
    base_table = base_table_match.group(1) if base_table_match else ""
    for col_entry in cols:
        if len(col_entry) == 2:
            alias, col = col_entry
        else:
            alias, col = "", col_entry[0]
        base = alias or base_table
        lineage.append({
            "source_table": base,
            "source_column": col,
            "destination_table": cte_name,
            "destination_column": col
        })

# Process final SELECT in last CTE or query
final_cte = list(cte_map.keys())[-1]
final_sql = cte_map[final_cte]
final_columns = extract_columns_from_select(final_sql)
alias_map.update({final_cte: final_cte})
lineage += resolve_column_sources(final_columns, alias_map, "detailed_sales")

# ---- OUTPUT ----
df = pd.DataFrame(lineage)
df.to_csv("dynamic_sql_lineage.csv", index=False)
print("Lineage saved to dynamic_sql_lineage.csv")
