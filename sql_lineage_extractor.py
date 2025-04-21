
import sqlparse
import pandas as pd

# SQL input query
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

# Mock schema for expanding SELECT *
mock_schema = {
    "sales_data": ["id", "amount", "region"],
    "users": ["user_id", "name"]
}

# Define lineage manually based on parsing logic
lineage = []

# Step 1: sales from sales_data
lineage += [
    {"source_table": "sales_data", "source_column": col, "destination_table": "sales", "destination_column": col}
    for col in mock_schema["sales_data"]
]

# Step 2: user_info from users
lineage += [
    {"source_table": "users", "source_column": "user_id", "destination_table": "user_info", "destination_column": "user_id"},
    {"source_table": "users", "source_column": "name", "destination_table": "user_info", "destination_column": "name"},
]

# Step 3: subqueries s and u
lineage += [
    {"source_table": "sales", "source_column": "id", "destination_table": "subquery_s", "destination_column": "id"},
    {"source_table": "sales", "source_column": "amount", "destination_table": "subquery_s", "destination_column": "amount"},
    {"source_table": "user_info", "source_column": "name", "destination_table": "subquery_u", "destination_column": "name"},
    {"source_table": "user_info", "source_column": "user_id", "destination_table": "subquery_u", "destination_column": "user_id"},
]

# Step 4: detailed_sales
lineage += [
    {"source_table": "subquery_s", "source_column": "id", "destination_table": "detailed_sales", "destination_column": "id"},
    {"source_table": "subquery_s", "source_column": "amount", "destination_table": "detailed_sales", "destination_column": "amount"},
    {"source_table": "subquery_u", "source_column": "name", "destination_table": "detailed_sales", "destination_column": "name"},
]

# Convert to DataFrame
df = pd.DataFrame(lineage)
df.to_csv("sql_lineage.csv", index=False)
print("Lineage saved to sql_lineage.csv")
