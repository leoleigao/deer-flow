"""LangGraph node that assembles a Markdown table guide."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Mapping

try:
    from langgraph.prebuilt.chat_agent_executor import AgentState
except Exception:  # pragma: no cover - fallback when langgraph not installed
    AgentState = Mapping[str, Any]  # type: ignore[misc, assignment]

try:  # pragma: no cover - optional dependency
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
except Exception:  # pragma: no cover - jinja2 missing
    Environment = None  # type: ignore
    FileSystemLoader = StrictUndefined = None  # type: ignore

try:
    from langgraph.prebuilt import agent_node  # type: ignore
except Exception:  # pragma: no cover - fallback when langgraph not installed

    def agent_node(cls=None):
        return cls if cls is not None else (lambda x: x)


logger = logging.getLogger(__name__)
TEMPLATE_PATH = Path("prompts/my_agents/table/reporter.md")

try:  # pragma: no cover - optional dependency
    import mdformat
except Exception:  # pragma: no cover - missing formatter
    mdformat = None  # type: ignore


@agent_node
class TableReporter:
    """Node to compile research insights into a table guide."""

    def __call__(self, state: AgentState | Mapping[str, Any]) -> dict[str, Any]:
        table_name = state.get("table_name", "unknown")
        locale = state.get("locale", "en-US")
        report_parts = state.get("report_parts")

        if not report_parts:
            guide = "No insights found\n"
        else:
            if Environment is None:
                guide = TEMPLATE_PATH.read_text()
                for key, val in {
                    "table_name": table_name,
                    "locale": locale,
                    **report_parts,
                }.items():
                    guide = guide.replace(f"{{{{ {key} }}}}", str(val))
            else:
                env = Environment(
                    loader=FileSystemLoader(str(TEMPLATE_PATH.parent)),
                    autoescape=False,
                    undefined=StrictUndefined,
                    trim_blocks=True,
                    lstrip_blocks=True,
                )
                template = env.get_template(TEMPLATE_PATH.name)
                guide = template.render(
                    table_name=table_name, locale=locale, **report_parts
                )

            guide = guide.replace("# Key Columns", "## Key Columns")
            if mdformat is not None:
                try:
                    guide = mdformat.text(guide)
                except Exception as exc:  # pragma: no cover - formatting failure
                    logger.warning(f"mdformat failed: {exc}")
            if not guide.endswith("\n"):
                guide += "\n"

        result = dict(state)
        result["table_guide_md"] = guide
        logger.info(f"[Reporter] Assembled guide for {table_name} ({len(guide)} chars)")
        return result
