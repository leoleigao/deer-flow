from datetime import date

from src.my_agents.table_research.merge_insights import merge_insights


def test_merge_insights_dedup_and_rank(monkeypatch):
    chunks = [
        {
            "insights": ["<INSIGHT_1> col:ad_id", "<INSIGHT_2> join"],
            "usage_examples": ["select *", "count"],
        },
        {
            "insights": ["  <INSIGHT_1> col:ad_id", "<INSIGHT_3> no owner"],
            "usage_examples": ["select *"],
        },
    ]
    glean_docs = [
        {"last_updated": "2024-06-05"},
        {"last_updated": "2024-05-20"},
    ]

    class FakeDate(date):
        @classmethod
        def today(cls):  # type: ignore[override]
            return date(2024, 6, 7)

    monkeypatch.setattr("src.my_agents.table_research.merge_insights.date", FakeDate)

    result = merge_insights(chunks, glean_docs)
    assert result["insights"] == [
        "<INSIGHT_1> col:ad_id",
        "<INSIGHT_2> join",
        "<INSIGHT_3> no owner",
    ]
    assert result["usage_examples"] == ["select *", "count"]
    assert result["freshness_sla"] == "hot"
