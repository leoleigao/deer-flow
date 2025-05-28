# ADR: Table-Deep-Research (TDR) Agents — Project Context

**Date:** May 26, 2025  
**Last Updated:** May 27, 2025  
**Status:** Accepted

## Context

We are extending the open-source [ByteDance DeerFlow](https://github.com/bytedance/deer-flow) framework to support **heavy table-centric analysis** and **report generation** workflows. This extension is collectively referred to as **Table-Deep-Research (TDR) Agents**.

Key points:

1. **Upstream Alignment:**

   * DeerFlow is under active development. We mirror upstream `main` and merge it nightly into our `develop` branch.
   * Our fork policy ensures minimal divergence: new functionality resides under `src/my_agents/` and `plugins/`.

2. **Scope of TDR Agents:**

   * **Tabular Data**: Provide specialized multi-step analyses for big tables (like `tracking.AdClickEvent`).
   * **LLM Workflow**: Introduce prompt templates and agent nodes specifically for table introspection, gleaning insights, and generating usage documentation.
   * **Stub-Mode Operation**: During initial development, we connect to a local JSON fixture store instead of hitting a real Glean or other knowledge store.

3. **Design & Implementation Outline:**

   * Agents, prompts, and tools are self-contained under new modules.
   * Enhanced concurrency (async tasks) to handle large volumes of doc chunks.
   * Coverage & lint are enforced at ≥ 90 %.

4. **Expected Output & Testing:**

   * TDR Agents produce structured data that feed into a final Markdown or HTML report.
   * Unit tests, integration tests, and "golden-flow" tests ensure consistent behavior across code updates.

## Decision

1. **Extend DeerFlow via a Non-Invasive Approach**

   * Core DeerFlow code is untouched (read-only); TDR logic goes under `src/my_agents/`, with adjacency where needed (e.g. new prompts in `prompts/my_agents/table/`).

2. **Add a Specialized Table-Research Graph**

   * A LangGraph pipeline that orchestrates:

     1. **Planner**: Decomposes tasks into steps.
     2. **TableResearcher**: Searches knowledge base (stub mode for now) and extracts insights using LLM.
     3. **Reporter**: Produces a final, structured Markdown or HTML summary using Jinja2 templates.

3. **Use "Stub Mode" by Default for Data Sources**

   * Local JSON fixtures under `tests/fixtures/glean/<table_name>.json`.
   * `USE_GLEAN_STUB=true` in `.env.example` so we avoid real knowledge base calls until production needs.
   * **Important**: Stub mode only affects the data source (Glean), not the LLM. The system still requires a configured LLM (e.g., OpenAI API) to process the fixture data and extract insights.

4. **Maintain Upstream Sync**

   * A nightly GitHub Actions job rebases `develop` onto `main`.
   * If conflicts arise, merges must preserve minimal diffs from upstream code.

5. **Preserve Quality and Observability**

   * All new code must pass `pytest` with coverage ≥ 90 %.
   * LLM calls in unit tests are mocked via DummyLLM for deterministic testing.
   * We store partial or final state in typed dictionaries to facilitate logging and debugging with LangGraph/ LangSmith.

## Consequences

* **Clear Separation of Concerns**:
  TDR extends DeerFlow without cluttering the upstream code. External merges remain straightforward.

* **Reduced Risk & Faster Iteration**:
  Stub mode for Glean integration allows TDR team to develop and test offline. Real environment toggles (`USE_GLEAN_STUB=false`) can be tested in a separate environment.

* **LLM Dependency**:
  Even in stub mode, the system requires a functioning LLM service (configured in `conf.yaml`) to process fixture data and generate insights. This ensures realistic testing of the full pipeline.

* **Strict Quality Gates**:
  With comprehensive tests and coverage thresholds, TDR changes are less likely to introduce regressions or break existing logic.

* **Maintenance Overhead**:
  We must maintain alignment with upstream changes. The nightly rebase requires vigilance if upstream's architecture or package layout changes significantly.

* **Documentation & Onboarding**:
  Additional prompts, new folder structure, and config overlays require updated dev docs and ADR references for future contributors.

---

### Implementation Notes

1. **Reporter Template**: The reporter uses Jinja2 templates located in `prompts/my_agents/table/reporter.md`. These templates must use proper variable substitution (e.g., `{{ table_name }}`) rather than hardcoded values to ensure dynamic report generation.

2. **LLM Configuration**: The system uses `get_llm_by_type('basic')` which reads from `conf.yaml`. Default configuration uses OpenAI's GPT-3.5-turbo model.

3. **Logging**: Application logs can be configured to write to files (e.g., `fastapi_debug.log`) for debugging. Log files should be added to `.gitignore`.

---

### References

* [**ByteDance DeerFlow** (upstream)](https://github.com/bytedance/deer-flow)
* **TDR Agents Master Document** (internal Confluence)
* `conf.d/table_research.yaml` overlay
* `tests/fixtures/glean/` for stub data
* CI pipeline in `.github/workflows/ci.yml`
* `prompts/my_agents/table/` for prompt templates

### Fixture Schema

Stub search results live under `tests/fixtures/glean/`. Each file is named
`<table_name>.json` and contains an array of documents. Every document carries
these mandatory fields:

```
doc_id        # unique across the corpus
title         # human readable title
doc_type      # schema | wiki | dashboard | runbook | lineage | notebook
table_name    # the table it references
description   # short summary
tags          # list of strings
url           # link to the source (Confluence, Grafana, etc.)
```

Optional blocks (e.g. `columns`, `lineage`, `metrics`, `sample_query`) add
realism so later agents can reason about freshness or popularity.

---

> **Note**: This ADR is a concise snapshot of the TDR Agents context and the key architecture choices. For detailed implementation steps (including code snippets, prompts, node definitions), refer to the "Table-Deep-Research Agent — Detailed Design & Implementation Guide" and your repository's `src/my_agents/table_research/` folder.
