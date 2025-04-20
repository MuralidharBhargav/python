import streamlit as st
from typing import Dict, List, Tuple
from graphviz import Digraph
import streamlit.components.v1 as components
from sqlglot import parse_one, exp

# --- Updated sqlglot lineage extractor (no main) ---
def extract_lineage_with_sqlglot_no_main(sql: str, schema: Dict[str, List[str]]) -> Tuple[
    Dict[str, List[str]], Dict[str, List[Tuple[str, str]]], Dict[str, str]]:

    parsed = parse_one(sql)
    cte_columns = {}
    cte_edges = {}
    alias_map = {}

    def resolve_columns(select_exp, alias_lookup):
        columns = []
        for col_exp in select_exp.expressions:
            if isinstance(col_exp, exp.Star):
                for alias, table in alias_lookup.items():
                    for col in schema.get(table, []):
                        columns.append(f"{alias}.{col}")
            elif isinstance(col_exp, exp.Alias):
                inner = col_exp.this
                if isinstance(inner, exp.Column):
                    columns.append(f"{inner.table}.{inner.name}")
            elif isinstance(col_exp, exp.Column):
                if col_exp.table:
                    columns.append(f"{col_exp.table}.{col_exp.name}")
                else:
                    columns.append(col_exp.name)
        return columns

    def extract_from_select(select_exp, cte_name=None, parent_sources=None):
        alias_lookup = {}
        sources = []

        for from_exp in select_exp.find_all(exp.From):
            for table_ref in from_exp.find_all(exp.Table):
                alias = table_ref.alias_or_name
                alias_lookup[alias] = table_ref.name
                sources.append((table_ref.name, alias))

        for join_exp in select_exp.find_all(exp.Join):
            table_ref = join_exp.this
            if isinstance(table_ref, exp.Subquery):
                sub_select = table_ref.unnest()
                sub_alias = table_ref.alias_or_name
                sub_name = f"subquery_{sub_alias}"
                alias_map[sub_alias] = "subquery"
                sub_cols = resolve_columns(sub_select, alias_lookup)
                cte_columns[sub_alias] = sub_cols
                parent_link = [(src, sub_alias) for src, _ in (parent_sources or [])]
                cte_edges[sub_alias] = parent_link
                alias_lookup[sub_alias] = sub_name
                sources.append((sub_name, sub_alias))
            elif isinstance(table_ref, exp.Table):
                alias = table_ref.alias_or_name
                alias_lookup[alias] = table_ref.name
                sources.append((table_ref.name, alias))

        columns = resolve_columns(select_exp, alias_lookup)
        if cte_name:
            cte_columns[cte_name] = columns
            cte_edges[cte_name] = sources

    for cte in parsed.find_all(exp.CTE):
        extract_from_select(cte.this, cte.alias)

    final_select = parsed.find(exp.Select)
    if final_select:
        sources = list(final_select.find_all(exp.Table))
        if len(sources) > 1 or final_select.expressions[0].sql() != "*":
            extract_from_select(final_select, cte_name="main")

    return cte_columns, cte_edges, alias_map

# --- SVG renderer ---
def build_svg_graphviz_sqlglot(
    cte_columns: Dict[str, List[str]],
    cte_edges: Dict[str, List[Tuple[str, str]]],
    alias_map: Dict[str, str],
    schema: Dict[str, List[str]],
    selected_field: str
) -> str:
    graph = Digraph(format='svg')
    graph.attr(rankdir='LR', fontname="Arial", nodesep='0.8')

    relevant_nodes = set()

    if selected_field == "All Fields":
        relevant_nodes.update(cte_columns.keys())
        relevant_nodes.update(schema.keys())
    else:
        def find_field_node(field):
            for node, cols in cte_columns.items():
                if any(field in col for col in cols):
                    return node
            return None

        def dfs(node):
            if node in relevant_nodes:
                return
            relevant_nodes.add(node)
            for source, _ in cte_edges.get(node, []):
                dfs(source)

        start_node = find_field_node(selected_field)
        if start_node:
            dfs(start_node)

    for node in relevant_nodes:
        cols = cte_columns.get(node, schema.get(node, []))

        if selected_field != "All Fields":
            cols = [c for c in cols if selected_field in c or selected_field.split('.')[-1] in c]

        label = f"<<B>{node}</B>"
        if cols:
            label += "<BR ALIGN='LEFT'/>" + "<BR ALIGN='LEFT'/>".join(cols)
        label += ">"
        fillcolor = (
            'lightblue' if node in alias_map
            else 'lightgray' if node in schema
            else 'white'
        )
        graph.node(node, shape='rect', style='filled', fillcolor=fillcolor, label=label)

    for target, sources in cte_edges.items():
        if target not in relevant_nodes:
            continue
        for source, alias in sources:
            if source in relevant_nodes:
                label = f"AS {alias}" if alias and alias != source else ""
                graph.edge(source, target, xlabel=label)

    return graph.pipe().decode('utf-8')

# --- Streamlit App UI ---
st.set_page_config(layout="wide")
st.title("🧠 SQL Lineage Visualizer (sqlglot, Clean Final Graph)")

sql_query = st.text_area("📥 Paste your SQL query:", height=300)

# Mock schema to resolve SELECT *
mock_schema = {
    "sales_data": ["id", "amount", "region"],
    "users": ["user_id", "name", "signup_date"]
}

if sql_query.strip():
    try:
        cte_columns, cte_edges, alias_map = extract_lineage_with_sqlglot_no_main(sql_query, mock_schema)
        all_fields = sorted(set(f for cols in cte_columns.values() for f in cols))
        selected_field = st.selectbox("🎯 Select field to trace lineage:", ["All Fields"] + all_fields)
        svg = build_svg_graphviz_sqlglot(
            cte_columns, cte_edges, alias_map, mock_schema, selected_field
        )
        components.html(svg, height=600, scrolling=True)
    except Exception as e:
        st.error(f"⚠️ Error parsing SQL: {e}")
else:
    st.info("Paste a SQL query above to visualize lineage.")
