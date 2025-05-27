"""LangGraph workflow wiring for Table-Deep-Research agents."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any
import asyncio

try:
    from langgraph.graph import END, START, StateGraph
except Exception:  # pragma: no cover - fallback when langgraph not installed

    class _DummyWorkflow:
        def __init__(self, nodes):
            self.nodes = nodes

        def invoke(self, state: dict[str, Any]) -> dict[str, Any]:
            for node in self.nodes:
                state.update(node(state))
            return state

    class StateGraph:
        def __init__(self, _state):
            self._nodes = []

        def add_node(self, _name: str, node):
            self._nodes.append(node)

        def add_edge(self, *_args, **_kwargs):
            pass

        def compile(
            self, max_parallel: int | None = None
        ):  # pragma: no cover - simple stub
            return _DummyWorkflow(self._nodes)

    START = END = None  # type: ignore

from .table_planner import TablePlanner
from .table_researcher import TableResearcher
from .table_reporter import TableReporter
from src.config.loader import load_yaml_config
from .utils import log_stub_once

logger = logging.getLogger("tdr.table_graph")


@dataclass
class TableResearchState:
    """Aggregate state for the table-deep-research workflow."""

    table_name: str
    plan: list[dict[str, Any]] | None = None
    doc_chunks: list[str] | None = None
    insights: dict[str, Any] | None = None
    report_parts: dict[str, Any] | None = None
    table_guide_md: str | None = None


def build_graph(max_parallel: int = 4):
    """Create and compile the table research graph."""
    planner = TablePlanner()
    researcher = TableResearcher()
    reporter = TableReporter()

    async def planner_node(state: TableResearchState) -> dict:
        result = await planner({"table_name": state.table_name})
        return result

    async def researcher_node(state: TableResearchState) -> dict:
        result = await researcher(
            {"table_name": state.table_name, "plan": state.plan or []}
        )
        return result

    def reporter_node(state: TableResearchState) -> dict:
        result = reporter(
            {"table_name": state.table_name, "report_parts": state.report_parts or {}}
        )
        return result

    builder = StateGraph(TableResearchState)
    builder.add_node("planner", planner_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("reporter", reporter_node)
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "reporter")
    builder.add_edge("reporter", END)
    return builder.compile()


async def arun_graph(table_name: str, *, max_docs: int | None = None) -> str:
    """Async: Execute the graph and return the Markdown report."""
    conf = load_yaml_config("conf.d/table_research.yaml").get("table_research", {})
    if max_docs is not None:
        conf["max_docs"] = max_docs
    use_stub = conf.get("glean", {}).get("use_stub", True)
    logger.info(
        "Starting graph for %s (max_docs=%s, use_stub=%s)",
        table_name,
        conf.get("max_docs"),
        use_stub,
    )

    graph = build_graph()
    start = time.monotonic()
    result = await graph.ainvoke({"table_name": table_name})
    elapsed = time.monotonic() - start
    logger.info("Generated guide for %s in %.2fs", table_name, elapsed)
    return result.get("table_guide_md", "")


def run_graph(table_name: str, *, max_docs: int | None = None) -> str:
    """Sync: Execute the graph and return the Markdown report."""
    return asyncio.run(arun_graph(table_name, max_docs=max_docs))
