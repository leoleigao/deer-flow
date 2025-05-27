"""Table-Deep-Research agents and utilities."""

try:
    from .table_researcher import TableResearcher
except Exception:  # pragma: no cover - optional when deps missing
    TableResearcher = None  # type: ignore[misc]

from .table_reporter import TableReporter
from .table_planner import TablePlanner
from .tools import GleanSearch
from .graph import run_graph


def run_table_deep_research(table_name: str, *, max_docs: int | None = None) -> str:
    """Run the table-deep-research workflow and return Markdown text."""
    return run_graph(table_name, max_docs=max_docs)


def cli_main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run Table Deep Research")
    parser.add_argument("table_name")
    parser.add_argument("--max-docs", type=int, default=None)
    args = parser.parse_args()

    md = run_table_deep_research(args.table_name, max_docs=args.max_docs)
    print(md)


__all__ = [
    "TablePlanner",
    "TableResearcher",
    "TableReporter",
    "GleanSearch",
    "run_table_deep_research",
    "cli_main",
]
