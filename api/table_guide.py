"""HTTP route scaffold for table guide generation."""

from __future__ import annotations

from fastapi import APIRouter

from my_agents.table_research import run_table_deep_research

table_guide_router = APIRouter()


@table_guide_router.get("/table_guide")
async def get_table_guide(table: str):
    guide = run_table_deep_research(table)
    return {"table": table, "guide": guide}
