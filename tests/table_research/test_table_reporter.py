import logging
import types

from src.my_agents.table_research.table_reporter import TableReporter


def _setup_mdformat(monkeypatch, fn):
    """Replace mdformat.text with given function."""
    module = __import__(
        "src.my_agents.table_research.table_reporter",
        fromlist=["mdformat"],
    )
    monkeypatch.setattr(module, "mdformat", types.SimpleNamespace(text=fn))


def test_reporter_happy_path(monkeypatch, caplog):
    caplog.set_level(logging.INFO)

    def identity(text: str) -> str:
        return text

    _setup_mdformat(monkeypatch, identity)

    reporter = TableReporter()
    state = {
        "table_name": "demo.Table",
        "report_parts": {"key_columns": ["id"], "sample_queries": ["select 1"]},
    }
    out = reporter(state)

    assert out["table_guide_md"].startswith("# Overview")
    assert "## Key Columns" in out["table_guide_md"]
    assert out["table_guide_md"].endswith("\n")
    log_lines = [r.message for r in caplog.records if "[Reporter]" in r.message]
    assert len(log_lines) == 1


def test_reporter_empty_parts():
    reporter = TableReporter()
    out = reporter({"table_name": "demo.Table"})
    assert out["table_guide_md"] == "No insights found\n"


def test_mdformat_failure(monkeypatch, caplog):
    caplog.set_level(logging.WARNING)

    def boom(_: str) -> str:
        raise RuntimeError("fail")

    _setup_mdformat(monkeypatch, boom)

    reporter = TableReporter()
    state = {"table_name": "demo.Table", "report_parts": {"key_columns": ["id"]}}
    out = reporter(state)
    assert out["table_guide_md"].startswith("# Overview")
    warn_lines = [r.message for r in caplog.records if "mdformat failed" in r.message]
    assert len(warn_lines) == 1
