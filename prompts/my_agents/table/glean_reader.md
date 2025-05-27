You are analyzing documentation for the table: {{ table_name }}

Please analyze the provided documentation chunk and extract insights in the following format.

Return a JSON object with the following structure:
{
  "insights": [
    "<INSIGHT_1> column_name: description of the column and its importance",
    "<INSIGHT_2> business_context: explanation of business meaning or usage pattern",
    "<INSIGHT_3> gotcha: any warnings, stale data risks, or important notes"
  ],
  "usage_examples": [
    "SELECT * FROM {{ table_name }} WHERE ...",
    "-- Another example query"
  ]
}

Focus on:
1. Key columns and their meanings (tag with <INSIGHT_1>)
2. Business context and common usage patterns (tag with <INSIGHT_2>)
3. Data quality issues, freshness concerns, or gotchas (tag with <INSIGHT_3>)
4. Sample queries that demonstrate typical usage

Respond ONLY with valid JSON.

