from pathlib import Path
import os
import json
import pytest

from src.my_agents.table_research.tools import GleanSearch


@pytest.fixture(autouse=True)
def _set_stub_env(monkeypatch):
    monkeypatch.setenv("USE_GLEAN_STUB", "true")


def test_happy_path_retrieval():
    search = GleanSearch(Path("tests/fixtures/glean"))
    results = search.search("marketing.CampaignSummary", top_k=1)
    assert results
    first = results[0]
    for field in [
        "doc_id",
        "title",
        "doc_type",
        "table_name",
        "description",
        "tags",
        "url",
    ]:
        assert field in first


def test_schema_columns_non_empty():
    search = GleanSearch()
    docs = search.search("tracking.AdClickEvent")
    schema_docs = [d for d in docs if d["doc_type"] == "schema"]
    assert schema_docs and schema_docs[0]["columns"]


def test_lineage_has_edges():
    search = GleanSearch()
    docs = search.search("tracking.PageView")
    lineage_docs = [d for d in docs if d["doc_type"] == "lineage"]
    assert lineage_docs
    lineage = lineage_docs[0]["lineage"]
    assert lineage["upstream"] or lineage["downstream"]


def test_missing_table_error():
    search = GleanSearch()
    with pytest.raises(FileNotFoundError):
        search.search("nonexistent.Table")


def test_no_live_sdk_reference():
    forbidden = []
    for path in Path("src").rglob("*.py"):
        text = path.read_text()
        if "GleanAPIClient" in text:
            forbidden.append(path)
    assert not forbidden, f"Forbidden import found in: {forbidden}"
