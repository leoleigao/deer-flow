import logging
import os

import pytest

from my_agents.table_research import run_table_deep_research


@pytest.mark.e2e
@pytest.mark.parametrize("table", ["tracking.AdClickEvent", "marketing.CampaignSummary"])
def test_run_table_deep_research_e2e(monkeypatch, caplog, table):
    if os.getenv("USE_GLEAN_STUB", "true").lower() != "true":
        pytest.skip("Glean stub disabled")
    caplog.set_level(logging.INFO)
    monkeypatch.setenv("USE_GLEAN_STUB", "true")

    md = run_table_deep_research(table)
    assert md.startswith("# ")
    assert "## Key Columns" in md
    assert any("stub mode" in r.message.lower() for r in caplog.records)

