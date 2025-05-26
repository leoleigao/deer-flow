"""Stub search tool for loading table documents from local fixtures."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class GleanSearch:
    """Load search results from JSON fixtures when stub mode is enabled."""

    def __init__(self, fixtures_dir: Path | None = None) -> None:
        self.fixtures_dir = fixtures_dir or Path("tests/fixtures/glean")

    def search(self, table_name: str, top_k: int | None = None) -> list[dict[str, Any]]:
        """Return search hits for the given table from fixture files."""
        if os.getenv("USE_GLEAN_STUB", "true").lower() != "true":
            raise RuntimeError("GleanSearch stub active but USE_GLEAN_STUB!=true")

        file_path = self.fixtures_dir / f"{table_name}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Fixture not found for table: {table_name}")

        with file_path.open("r", encoding="utf-8") as f:
            docs: list[dict[str, Any]] = json.load(f)

        if top_k is not None:
            return docs[:top_k]
        return docs
