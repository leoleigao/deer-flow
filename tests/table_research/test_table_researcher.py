import json
import logging
import types

import pytest

from src.my_agents.table_research.table_researcher import TableResearcher


class DummyLLM:
    async def ainvoke(self, messages):
        return types.SimpleNamespace(
            content=json.dumps(
                {"insights": ["<INSIGHT_1> col:ad_id"], "usage_examples": ["select *"]}
            )
        )


@pytest.mark.asyncio
async def test_table_researcher_flow(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    monkeypatch.setenv("USE_GLEAN_STUB", "true")
    monkeypatch.setenv("LLM_PAR", "1")

    researcher = TableResearcher()
    researcher.cfg["max_docs"] = 1
    researcher.llm = DummyLLM()

    state = {"table_name": "tracking.AdClickEvent"}
    first = await researcher(state)
    await researcher(state)

    assert first["glean_docs"]
    assert first["report_parts"]["key_columns"] == ["col:ad_id"]
    assert first["report_parts"]["sample_queries"] == ["select *"]
    log_lines = [r.message for r in caplog.records if "Operating in Glean" in r.message]
    assert len(log_lines) == 1
