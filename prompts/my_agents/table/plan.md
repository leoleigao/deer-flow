---
chunk_tokens: {{ chunk_tokens }}
---

As the Table Research Planner, break down analysis of **{{ table_name }}** into clear steps.
Return only a JSON array using these keys: `name` and `description`.

Steps to generate:
1. `review_schema` – gather column definitions and key metrics.
2. `map_lineage` – outline upstream and downstream relationships.
3. `analyse_usage` – list typical queries and dashboards.
4. `check_freshness` – note last update times and stale docs.
5. `compile_examples` – provide sample SQL snippets.

