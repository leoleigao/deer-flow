"""LangGraph node that creates a research plan for a table."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

try:
    from langgraph.prebuilt import agent_node
except Exception:  # pragma: no cover - fallback when langgraph not installed
    def agent_node(cls=None):
        return cls if cls is not None else (lambda x: x)

try:
    from langgraph.prebuilt.chat_agent_executor import AgentState
except Exception:  # pragma: no cover - fallback when langgraph not installed
    AgentState = dict  # type: ignore[misc, assignment]

from langchain_openai import ChatOpenAI

from src.config.loader import load_yaml_config
from src.prompts.template import apply_prompt_template
from .utils import log_stub_once

logger = logging.getLogger(__name__)


@agent_node
class TablePlanner:
    """Node that generates the analysis plan."""

    def __init__(self) -> None:
        conf = load_yaml_config(str(Path("conf.d/table_research.yaml")))
        self.cfg = conf.get("table_research", {})
        self.llm = ChatOpenAI(**self.cfg.get("llm", {}))
        self._logged = False

    async def __call__(self, state: AgentState) -> dict[str, Any]:
        if not self._logged:
            log_stub_once(logger)
            self._logged = True
        table_name = state["table_name"]
        messages = apply_prompt_template(
            "my_agents/table/plan",
            {
                "messages": [],
                "table_name": table_name,
                "chunk_tokens": self.cfg.get("chunk_tokens"),
            },
        )
        resp = await self.llm.ainvoke(messages)
        try:
            plan = json.loads(resp.content)
        except Exception:
            plan = []
        return {"plan": plan}
