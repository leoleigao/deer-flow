"""LangGraph node that creates a research plan for a table."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader

try:
    from langgraph.prebuilt import agent_node
except Exception:  # pragma: no cover - fallback when langgraph not installed

    def agent_node(cls=None):
        return cls if cls is not None else (lambda x: x)


try:
    from langgraph.prebuilt.chat_agent_executor import AgentState
except Exception:  # pragma: no cover - fallback when langgraph not installed
    AgentState = dict  # type: ignore[misc, assignment]

# For real LLM
from langchain_openai import ChatOpenAI

# Reuse DummyLLM from TableResearcher to avoid real API calls when USE_GLEAN_STUB=true
from .table_researcher import DummyLLM

from src.config.loader import load_yaml_config
from .utils import log_stub_once

logger = logging.getLogger(__name__)

# Create custom environment for my_agents prompts
my_agents_env = Environment(
    loader=FileSystemLoader(str(Path("prompts"))),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)


@agent_node
class TablePlanner:
    """Node that generates the analysis plan."""

    def __init__(self) -> None:
        conf = load_yaml_config(str(Path("conf.d/table_research.yaml")))
        self.cfg = conf.get("table_research", {})
        # If running in stub mode, use DummyLLM to avoid external API calls
        if self.cfg.get("glean", {}).get("use_stub", True):
            logger.info(
                "[TablePlanner] Initializing with DummyLLM due to USE_GLEAN_STUB=true."
            )
            self.llm = DummyLLM()
        else:
            logger.info("[TablePlanner] Initializing with real ChatOpenAI.")
            self.llm = ChatOpenAI(**self.cfg.get("llm", {}))
        self._logged = False

    async def __call__(self, state: AgentState) -> dict[str, Any]:
        if not self._logged:
            log_stub_once(logger)
            self._logged = True
        table_name = state["table_name"]

        # Use custom template loader
        template = my_agents_env.get_template("my_agents/table/plan.md")
        prompt = template.render(
            table_name=table_name,
            chunk_tokens=self.cfg.get("chunk_tokens"),
        )
        messages = [{"role": "system", "content": prompt}]

        resp = await self.llm.ainvoke(messages)
        try:
            plan = json.loads(resp.content)
        except Exception:
            plan = []
        return {"plan": plan}
