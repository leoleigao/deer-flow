# ADR: Table-Deep-Research (TDR) Agents — Project Context

**Date:** May 26, 2025
**Status:** Accepted
## Context

We are extending the open-source [ByteDance DeerFlow](https://github.com/bytedance/deer-flow) framework to support **heavy table-centric analysis** and **report generation** workflows. This extension is collectively referred to as **Table-Deep-Research (TDR) Agents**.

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
   * Coverage & lint are enforced at ≥ 90 %.

4. **Expected Output & Testing:**

   * TDR Agents produce structured data that feed into a final Markdown or HTML report.
   * Unit tests, integration tests, and “golden-flow” tests ensure consistent behavior across code updates.

## Decision

1. **Extend DeerFlow via a Non-Invasive Approach**

   * Core DeerFlow code is untouched (read-only); TDR logic goes under `src/my_agents/`, with adjacency where needed (e.g. new prompts in `prompts/my_agents/table/`).

2. **Add a Specialized Table-Research Graph**

   * A LangGraph pipeline that orchestrates:

     1. **Planner**: Decomposes tasks into steps.
     2. **TableResearcher**: Searches knowledge base (stub mode for now) and extracts insights.
     3. **Reporter**: Produces a final, structured Markdown or HTML summary.

3. **Use “Stub Mode” by Default**

   * Local JSON fixtures under `tests/fixtures/glean/<table_name>.json`.
   * `USE_GLEAN_STUB=true` in `.env.example` so we avoid real knowledge base calls until production needs.

4. **Maintain Upstream Sync**

   * A nightly GitHub Actions job rebases `develop` onto `main`.
   * If conflicts arise, merges must preserve minimal diffs from upstream code.

5. **Preserve Quality and Observability**

   * All new code must pass `pytest` with coverage ≥ 90 %.
   * LLM calls are tested via monkeypatched/mocked responses.
   * We store partial or final state in typed dictionaries to facilitate logging and debugging with LangGraph/ LangSmith.

## Consequences

* **Clear Separation of Concerns**:
  TDR extends DeerFlow without cluttering the upstream code. External merges remain straightforward.

* **Reduced Risk & Faster Iteration**:
  Stub mode for Glean integration allows TDR team to develop and test offline. Real environment toggles (`USE_GLEAN_STUB=false`) can be tested in a separate environment.

* **Strict Quality Gates**:
  With comprehensive tests and coverage thresholds, TDR changes are less likely to introduce regressions or break existing logic.

* **Maintenance Overhead**:
  We must maintain alignment with upstream changes. The nightly rebase requires vigilance if upstream’s architecture or package layout changes significantly.

* **Documentation & Onboarding**:
  Additional prompts, new folder structure, and config overlays require updated dev docs and ADR references for future contributors.

---

### References

* [**ByteDance DeerFlow** (upstream)](https://github.com/bytedance/deer-flow)
* **TDR Agents Master Document** (internal Confluence)
* `conf.d/table_research.yaml` overlay
* `tests/fixtures/glean/` for stub data
* CI pipeline in `.github/workflows/ci.yml`

---

> **Note**: This ADR is a concise snapshot of the TDR Agents context and the key architecture choices. For detailed implementation steps (including code snippets, prompts, node definitions), refer to the “Table-Deep-Research Agent — Detailed Design & Implementation Guide” and your repository’s `src/my_agents/table_research/` folder.
