"""Table-Deep-Research agents and utilities."""

try:
    from .table_researcher import TableResearcher
except Exception:  # pragma: no cover - optional when deps missing
    TableResearcher = None  # type: ignore[misc]

from .table_reporter import TableReporter
from .tools import GleanSearch

__all__ = ["TableResearcher", "TableReporter", "GleanSearch"]
