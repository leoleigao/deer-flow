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
from src.llms.llm import get_llm_by_type

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
        logger.info("[TablePlanner] Initializing LLM via get_llm_by_type('basic').")
        self.llm = get_llm_by_type("basic")
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
