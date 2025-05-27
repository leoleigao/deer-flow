"""LangGraph node that processes Glean docs into structured insights."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader
import types  # For SimpleNamespace in DummyLLM

try:
    from langgraph.prebuilt import agent_node
except Exception:  # pragma: no cover - fallback when langgraph not installed

    def agent_node(cls=None):
        return cls if cls is not None else (lambda x: x)


from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_openai import ChatOpenAI

from src.config.loader import load_yaml_config
from .smart_split import smart_split
from .merge_insights import merge_insights
from .tools import GleanSearch
from .utils import log_stub_once

logger = logging.getLogger(__name__)

# Create custom environment for my_agents prompts
my_agents_env = Environment(
    loader=FileSystemLoader(str(Path("prompts"))),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)


# Define DummyLLM for stub mode
class DummyLLM:
    async def ainvoke(self, messages: list[dict[str, str]]) -> types.SimpleNamespace:
        # Extract table_name from system prompt if needed for more dynamic stubs
        # For now, a generic valid JSON response structure
        logger.info("[TableResearcher] Using DummyLLM to simulate LLM response.")
        return types.SimpleNamespace(
            content=json.dumps(
                {
                    "insights": [
                        "<INSIGHT_1> session_id: Dummy key identifier for user sessions.",
                        "<INSIGHT_2> event.FunnelStep is often joined with other tables for dummy analysis.",
                        "<INSIGHT_3> Dummy data is always fresh!",
                    ],
                    "usage_examples": [
                        "SELECT * FROM {{ table_name }} WHERE dummy_condition = true;",
                        "-- Another dummy query for {{ table_name }}",
                    ],
                }
            )
        )


@agent_node
class TableResearcher:
    """Node for extracting insights from table documentation."""

    def __init__(self) -> None:
        conf = load_yaml_config(str(Path("conf.d/table_research.yaml")))
        self.cfg = conf.get("table_research", {})
        self.search = GleanSearch()

        if self.cfg.get("glean", {}).get("use_stub", True):
            logger.info(
                "[TableResearcher] Initializing with DummyLLM due to USE_GLEAN_STUB=true."
            )
            self.llm = DummyLLM()
        else:
            logger.info("[TableResearcher] Initializing with real ChatOpenAI.")
            self.llm = ChatOpenAI(**self.cfg.get("llm", {}))

        self.semaphore = asyncio.Semaphore(int(os.getenv("LLM_PAR", 4)))
        self._logged_stub = False

    async def __call__(self, state: AgentState) -> dict[str, Any]:
        if not self._logged_stub:
            log_stub_once(logger)
            self._logged_stub = True

        table_name = state["table_name"]
        docs = self.search.search(table_name, top_k=self.cfg.get("max_docs"))

        chunks = []
        for i, doc in enumerate(docs):
            text = json.dumps(doc, ensure_ascii=False)
            for j, chunk in enumerate(
                smart_split(text, self.cfg.get("chunk_tokens", 2048))
            ):
                chunks.append((i, j, chunk))

        async def run_chunk(chunk: str) -> dict[str, Any]:
            async with self.semaphore:
                # Use custom template loader
                template = my_agents_env.get_template("my_agents/table/glean_reader.md")
                prompt = template.render(
                    table_name=table_name,
                    chunk_tokens=self.cfg.get("chunk_tokens"),
                )
                messages = [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": chunk},
                ]
                resp = await self.llm.ainvoke(messages)
                try:
                    content = resp.content
                    logger.info(
                        f"[TableResearcher] Raw LLM content for chunk: {content}"
                    )
                    # Remove markdown code blocks if present
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.startswith("```"):
                        content = content[3:]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                    parsed_output = json.loads(content)
                    logger.info(
                        f"[TableResearcher] Parsed LLM output for chunk: {parsed_output}"
                    )
                    return parsed_output
                except Exception as e:
                    logger.error(
                        f"[TableResearcher] Error parsing LLM output: {e}. Raw content: {content}"
                    )
                    return {"insights": [], "usage_examples": []}

        outputs = await asyncio.gather(*(run_chunk(c) for _, _, c in chunks))
        aggregated = merge_insights(outputs, docs)
        logger.info(f"[TableResearcher] Aggregated insights: {aggregated}")
        report_parts = self._derive_report_parts(aggregated)
        logger.info(f"[TableResearcher] Derived report parts: {report_parts}")

        return {
            "glean_docs": docs,
            "doc_insights": aggregated,
            "report_parts": report_parts,
        }

    def _derive_report_parts(self, aggregated: dict[str, Any]) -> dict[str, Any]:
        key_cols: list[str] = []
        business: list[str] = []
        gotchas: list[str] = []
        for ins in aggregated.get("insights", []):
            text = ins.strip()
            upper = text.upper()
            if upper.startswith("<INSIGHT_1>"):
                key_cols.append(text.split(">", 1)[-1].strip())
            elif upper.startswith("<INSIGHT_2>"):
                business.append(text.split(">", 1)[-1].strip())
            elif upper.startswith("<INSIGHT_3>"):
                gotchas.append(text.split(">", 1)[-1].strip())
        parts = {
            "key_columns": key_cols,
            "business_meanings": business,
            "gotchas": gotchas,
            "sample_queries": aggregated.get("usage_examples", []),
        }
        return {k: v for k, v in parts.items() if v}
