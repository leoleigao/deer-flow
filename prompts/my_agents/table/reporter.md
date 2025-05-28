# Overview
This guide provides documentation for the **{{ table_name }}** table.

{% if key_columns %}
## Key Columns
{% for column in key_columns %}
- {{ column }}
{% endfor %}
{% endif %}

{% if business_meanings %}
## Business Context
{% for meaning in business_meanings %}
- {{ meaning }}
{% endfor %}
{% endif %}

{% if gotchas %}
## Governance Notes
{% for gotcha in gotchas %}
- {{ gotcha }}
{% endfor %}
{% endif %}

{% if sample_queries %}
## Sample Queries
{% for query in sample_queries %}
```sql
{{ query }}
```
{% endfor %}
{% endif %}

