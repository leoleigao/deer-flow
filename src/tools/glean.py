import json
import logging
import os
from pathlib import Path
from typing import Annotated

try:
    from langchain_core.tools import tool
except Exception:  # pragma: no cover - fallback for missing dependency
    def tool(func=None, *, name=None, description=None):
        def decorator(f):
            f.name = name or f.__name__
            f.description = description
            return f

        if func is not None:
            return decorator(func)
        return decorator

from .decorators import log_io

logger = logging.getLogger(__name__)

FIXTURE_DIR = Path(
    os.getenv(
        "GLEAN_FIXTURE_DIR",
        Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "glean_data",
    )
)


@tool
@log_io
def glean_search_tool(
    table_name: Annotated[str, "Name of the table to lookup."],
) -> str:
    """Lookup table documentation from local Glean fixtures."""
    file_path = FIXTURE_DIR / f"{table_name}.json"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        docs = data.get("docs", [])
        return json.dumps({"table": table_name, "docs": docs}, ensure_ascii=False)
    except FileNotFoundError:
        logger.error("Glean fixture for %s not found", table_name)
        return f"No docs found for {table_name}"
    except Exception as e:
        logger.error("Error loading docs for %s: %s", table_name, e)
        return f"Error loading docs for {table_name}: {e}"
