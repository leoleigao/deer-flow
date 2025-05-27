"""HTTP route scaffold for table guide generation."""

from __future__ import annotations

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

from src.my_agents.table_research import run_table_deep_research
from src.my_agents.table_research.graph import arun_graph

table_guide_router = APIRouter()


@table_guide_router.get("/table_guide")
async def get_table_guide(table: str):
    """Generate a table guide for the specified table."""
    try:
        guide = await arun_graph(table)
        return {"table": table, "guide": guide}
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"No fixture data found for table: {table}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate guide: {str(e)}"
        )


@table_guide_router.get("/fixtures_index")
async def get_fixtures_index():
    """Get a list of available table fixtures for the dropdown."""
    fixtures_dir = Path("tests/fixtures/glean")

    if not fixtures_dir.exists():
        return {"tables": []}

    tables = []
    for fixture_file in fixtures_dir.glob("*.json"):
        table_name = fixture_file.stem
        try:
            # Read the first document to get metadata
            with fixture_file.open("r", encoding="utf-8") as f:
                docs = json.load(f)
                if docs and isinstance(docs, list) and len(docs) > 0:
                    first_doc = docs[0]
                    tables.append(
                        {
                            "name": table_name,
                            "title": first_doc.get("title", table_name),
                            "description": first_doc.get("description", ""),
                            "doc_count": len(docs),
                        }
                    )
                else:
                    tables.append(
                        {
                            "name": table_name,
                            "title": table_name,
                            "description": "",
                            "doc_count": 0,
                        }
                    )
        except Exception:
            # If we can't read the file, still include it with minimal info
            tables.append(
                {
                    "name": table_name,
                    "title": table_name,
                    "description": "Unable to read fixture data",
                    "doc_count": 0,
                }
            )

    # Sort by table name for consistent ordering
    tables.sort(key=lambda x: x["name"])
    return {"tables": tables}
