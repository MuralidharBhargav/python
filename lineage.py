import streamlit as st
import re
from typing import Dict, List, Tuple
from graphviz import Digraph
import streamlit.components.v1 as components

def extract_lineage(sql: str, schema: Dict[str, List[str]]) -> Tuple[
    Dict[str, List[str]], Dict[str, List[Tuple[str, str]]], Dict[str, str]]:
    cte_pattern = re.compile(r'(\w+)\s+AS\s+\((.*?)\)(?=,|\s+SELECT|\s*$)', re.DOTALL | re.IGNORECASE)
    subquery_pattern = re.compile(r'\(\s*SELECT\s+(.*?)\s+FROM\s+(\w+)\s*\)\s+AS\s+(\w+)', re.IGNORECASE | re.DOTALL)

    ctes = dict((name.strip(), body) for name, body in cte_pattern.findall(sql))
    cte_columns = {}
    cte_edges = {}
    alias_map = {}

    for cte_name, cte_body in ctes.items():
        used_sources = []
        alias_matches = re.findall(
            r'(FROM|JOIN)\s+(?:\((.*?)\)\s+AS\s+(\w+)|(?:(\w+)(?:\s+(?:AS\s+)?(\w+))?))',
            cte_body, re.IGNORECASE | re.DOTALL
        )

        alias_lookup = {}
        for _, subquery, sub_alias, table, table_alias in alias_matches:
            if subquery and sub_alias:
                alias_map[sub_alias] = "subquery"
                used_sources.append(("subquery", sub_alias))
                alias_lookup[sub_alias] = "subquery"
            elif table:
                alias = table_alias or table
                alias_lookup[alias.strip()] = table.strip()
                used_sources.append((table.strip(), alias.strip()))

        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', cte_body.strip(), re.IGNORECASE | re.DOTALL)
        columns = []

        if select_match:
            select_part = select_match.group(1)
            if '*' in select_part:
                for alias, table in alias_lookup.items():
                    source_cols = schema.get(table, []) if table not in cte_columns else [
                        col.split('.', 1)[-1] for col in cte_columns[table]]
                    columns.extend([f"{alias}.{col}" for col in source_cols])
            else:
                col_parts = select_part.split(',')
                for col in col_parts:
                    col = col.strip()
                    if '.' in col:
                        alias, colname = col.split('.', 1)
                        columns.append(f"{alias.strip()}.{colname.strip()}")
                    else:
                        columns.append(col)

        cte_columns[cte_name] = columns
        cte_edges[cte_name] = used_sources

    for select_cols, base_table, alias in subquery_pattern.findall(sql):
        base_table = base_table.strip()
        alias = alias.strip()
        selected_cols = [c.strip() for c in select_cols.split(',')]
        cte_columns[base_table] = schema.get(base_table, [])
        cte_columns[alias] = [f"{alias}.{col}" for col in selected_cols]
        cte_edges[alias] = [(base_table, alias)]
        alias_map[alias] = "subquery"

    return cte_columns, cte_edges, alias_map

def build_recursive_graph(
    cte_columns: Dict[str, List[str]],
    cte_edges: Dict[str, List[Tuple[str, str]]],
    alias_map: Dict[str, str],
    schema: Dict[str, List[str]],
    selected_field: str
) -> str:
    graph = Digraph(format='svg')
    graph.attr(rankdir='LR', fontname="Helvetica")

    if selected_field == "All Fields":
        relevant_nodes = set(cte_columns.keys()) | set(schema.keys())
    else:
        relevant_nodes = set()

        def find_field_node(field):
            for node, cols in cte_columns.items():
                if any(field in col for col in cols):
                    return node
            return None

        def trace_upstream(node):
            if node in relevant_nodes:
                return
            relevant_nodes.add(node)
            for source, _ in cte_edges.get(node, []):
                trace_upstream(source)

        start_node = find_field_node(selected_field)
        if start_node:
            trace_upstream(start_node)

    for node in relevant_nodes:
        cols = cte_columns.get(node, [])
        if node in schema:
            filtered = schema[node]  # Always show full fields from base tables
        elif selected_field != "All Fields":
            filtered = [col for col in cols if selected_field in col or selected_field.split('.')[-1] in col]
        else:
            filtered = cols

        label = f"<<B>{node}</B>"
        if filtered:
            label += "<BR ALIGN='LEFT'/>" + "<BR ALIGN='LEFT'/>".join(filtered)
        label += ">"
        fillcolor = (
            'lightblue' if node in alias_map
            else 'lightgray' if node in schema
            else 'white'
        )
        graph.node(node, shape='rect', style='filled', fillcolor=fillcolor, label=label)

    for table, cols in schema.items():
        if table not in relevant_nodes:
            label = f"<<B>{table}</B><BR ALIGN='LEFT'/>" + "<BR ALIGN='LEFT'/>".join(cols) + ">"
            graph.node(table, shape='rect', style='filled', fillcolor='lightgray', label=label)

    for target in relevant_nodes:
        for source, alias in cte_edges.get(target, []):
            if source in relevant_nodes:
                label = f"AS {alias}" if alias and alias != source else ""
                graph.edge(source, target, xlabel=label)

    return graph.pipe(format='svg').decode('utf-8')

# ---------------- Streamlit UI ----------------
st.set_page_config(layout="wide")
st.title("🧠 SQL Lineage Visualizer (CTEs + Subqueries + Field Filter)")

sql_query = st.text_area("📥 Paste your SQL query:", height=300)

mock_schema = {
    "sales_data": ["id", "amount", "region"],
    "users": ["user_id", "name", "signup_date"]
}

if sql_query.strip():
    cte_columns, cte_edges, alias_map = extract_lineage(sql_query, mock_schema)
    final_cte = list(cte_columns.keys())[-1]
    final_fields = cte_columns[final_cte]
    options = ["All Fields"] + final_fields
    selected_field = st.selectbox("🎯 Select a field to trace lineage (or All Fields):", options)
    svg = build_recursive_graph(cte_columns, cte_edges, alias_map, mock_schema, selected_field)
    components.html(svg, height=600, scrolling=True)
else:
    st.info("Paste your SQL above to begin.")
