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


def test_top_k_parameter():
    search = GleanSearch()
    # Test with top_k=2
    results = search.search("marketing.CampaignSummary", top_k=2)
    assert len(results) == 2

    # Test with top_k=None (should return all results)
    all_results = search.search("marketing.CampaignSummary")
    assert len(all_results) > 2

    # Test with top_k=0 (should return empty list)
    empty_results = search.search("marketing.CampaignSummary", top_k=0)
    assert len(empty_results) == 0

    # Test with top_k larger than available results
    large_k_results = search.search("marketing.CampaignSummary", top_k=100)
    assert len(large_k_results) == len(all_results)


def test_custom_fixtures_dir():
    """Test that custom fixtures directory is properly used."""
    custom_dir = Path("tests/fixtures/glean")
    search = GleanSearch(fixtures_dir=custom_dir)
    results = search.search("marketing.CampaignSummary")
    assert results
    assert len(results) > 0


def test_document_type_validation():
    """Test that all documents have valid doc_type values."""
    search = GleanSearch()
    valid_types = {"schema", "wiki", "dashboard", "runbook", "lineage", "notebook"}

    # Test all fixture files
    for table in [
        "marketing.CampaignSummary",
        "tracking.AdClickEvent",
        "tracking.PageView",
    ]:
        docs = search.search(table)
        for doc in docs:
            assert (
                doc["doc_type"] in valid_types
            ), f"Invalid doc_type in {table}: {doc['doc_type']}"


def test_required_fields_presence():
    """Test that all documents have all required fields."""
    search = GleanSearch()
    required_fields = {
        "doc_id",
        "title",
        "doc_type",
        "table_name",
        "description",
        "tags",
        "url",
    }

    # Test all fixture files
    for table in [
        "marketing.CampaignSummary",
        "tracking.AdClickEvent",
        "tracking.PageView",
    ]:
        docs = search.search(table)
        for doc in docs:
            missing_fields = required_fields - set(doc.keys())
            assert (
                not missing_fields
            ), f"Missing required fields in {table}: {missing_fields}"


def test_doc_id_uniqueness():
    """Test that doc_ids are unique across all documents."""
    search = GleanSearch()
    all_docs = []

    # Collect all documents from all fixture files
    for table in [
        "marketing.CampaignSummary",
        "tracking.AdClickEvent",
        "tracking.PageView",
    ]:
        all_docs.extend(search.search(table))

    # Check for duplicate doc_ids
    doc_ids = [doc["doc_id"] for doc in all_docs]
    assert len(doc_ids) == len(set(doc_ids)), "Duplicate doc_ids found"


def test_stub_mode_enforcement():
    """Test that stub mode is properly enforced."""
    search = GleanSearch()

    # Test with stub mode enabled (should work)
    results = search.search("marketing.CampaignSummary")
    assert results

    # Test with stub mode disabled (should raise error)
    with pytest.raises(
        RuntimeError, match="GleanSearch stub active but USE_GLEAN_STUB!=true"
    ):
        os.environ["USE_GLEAN_STUB"] = "false"
        search.search("marketing.CampaignSummary")


def test_fixture_file_loading():
    """Test that fixture files are properly loaded and parsed."""
    search = GleanSearch()

    # Test loading a known fixture file
    results = search.search("marketing.CampaignSummary")
    assert isinstance(results, list)
    assert all(isinstance(doc, dict) for doc in results)

    # Test that all expected doc_types are present
    doc_types = {doc["doc_type"] for doc in results}
    expected_types = {"schema", "wiki", "dashboard", "runbook"}
    assert (
        doc_types == expected_types
    ), f"Expected doc_types {expected_types}, got {doc_types}"

    # Test that all doc_ids follow the expected pattern
    for doc in results:
        parts = doc["doc_id"].split(".")
        assert len(parts) == 3, f"Invalid doc_id format: {doc['doc_id']}"
        assert parts[0] == "marketing"
        assert parts[1] == "CampaignSummary"
        assert parts[2] in expected_types
