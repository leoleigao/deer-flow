"""LangGraph node that processes Glean docs into structured insights."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

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
from src.prompts.template import apply_prompt_template

logger = logging.getLogger(__name__)


@agent_node
class TableResearcher:
    """Node for extracting insights from table documentation."""

    def __init__(self) -> None:
        conf = load_yaml_config(str(Path("conf.d/table_research.yaml")))
        self.cfg = conf.get("table_research", {})
        self.search = GleanSearch()
        self.llm = ChatOpenAI(**self.cfg.get("llm", {}))
        self.semaphore = asyncio.Semaphore(int(os.getenv("LLM_PAR", 4)))
        self._logged_stub = False

    async def __call__(self, state: AgentState) -> dict[str, Any]:
        if not self._logged_stub:
            mode = (
                "stub"
                if os.getenv("USE_GLEAN_STUB", "true").lower() == "true"
                else "live"
            )
            logger.info(f"Operating in Glean {mode} mode")
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
                messages = apply_prompt_template(
                    "my_agents/table/glean_reader",
                    {
                        "messages": [{"role": "user", "content": chunk}],
                        "table_name": table_name,
                        "chunk_tokens": self.cfg.get("chunk_tokens"),
                    },
                )
                resp = await self.llm.ainvoke(messages)
                try:
                    return json.loads(resp.content)
                except Exception:
                    return {"insights": [], "usage_examples": []}

        outputs = await asyncio.gather(*(run_chunk(c) for _, _, c in chunks))
        aggregated = merge_insights(outputs, docs)
        report_parts = self._derive_report_parts(aggregated)

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
