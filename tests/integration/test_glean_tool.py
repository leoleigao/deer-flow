import json
import os
from pathlib import Path

from src.tools.glean import glean_search_tool, FIXTURE_DIR


def test_glean_search_tool_found(tmp_path, monkeypatch):
    monkeypatch.setenv("GLEAN_FIXTURE_DIR", str(Path("tests/fixtures/glean_data")))
    result = glean_search_tool("users")
    data = json.loads(result)
    assert data["table"] == "users"
    assert any("account" in d for d in data["docs"])


def test_glean_search_tool_not_found(monkeypatch):
    monkeypatch.setenv("GLEAN_FIXTURE_DIR", str(Path("tests/fixtures/glean_data")))
    result = glean_search_tool("missing_table")
    assert "No docs found" in result
