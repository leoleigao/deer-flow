# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os

try:
    from .crawl import crawl_tool
except Exception:  # pragma: no cover - optional dependency missing
    crawl_tool = None

try:
    from .python_repl import python_repl_tool
except Exception:  # pragma: no cover
    python_repl_tool = None

try:
    from .glean import glean_search_tool
except Exception:  # pragma: no cover
    glean_search_tool = None

try:
    from .search import (
        tavily_search_tool,
        duckduckgo_search_tool,
        brave_search_tool,
        arxiv_search_tool,
    )
except Exception:  # pragma: no cover
    tavily_search_tool = duckduckgo_search_tool = brave_search_tool = arxiv_search_tool = None

try:
    from .tts import VolcengineTTS
except Exception:  # pragma: no cover
    VolcengineTTS = None
from src.config import SELECTED_SEARCH_ENGINE, SearchEngine

# Map search engine names to their respective tools
search_tool_mappings = {
    SearchEngine.TAVILY.value: tavily_search_tool,
    SearchEngine.DUCKDUCKGO.value: duckduckgo_search_tool,
    SearchEngine.BRAVE_SEARCH.value: brave_search_tool,
    SearchEngine.ARXIV.value: arxiv_search_tool,
}

web_search_tool = search_tool_mappings.get(SELECTED_SEARCH_ENGINE, tavily_search_tool)

__all__ = [
    "crawl_tool",
    "web_search_tool",
    "python_repl_tool",
    "glean_search_tool",
    "VolcengineTTS",
]
