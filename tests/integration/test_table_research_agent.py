from unittest.mock import MagicMock

from src.agents import table_research_agent


def test_table_research_agent_creation():
    assert hasattr(table_research_agent, "invoke")
    assert any("glean_search_tool" in t.name for t in table_research_agent.tools)


def test_table_research_agent_invocation(monkeypatch):
    # Patch model to return canned response
    dummy_model = MagicMock()
    dummy_model.invoke.return_value = "usage guide"
    monkeypatch.setattr(table_research_agent, "model", dummy_model)
    result = table_research_agent.invoke({"messages": []})
    assert result == "usage guide"
