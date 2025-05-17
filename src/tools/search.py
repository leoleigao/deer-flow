# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os

from langchain_community.tools import BraveSearch, DuckDuckGoSearchResults
from langchain_community.tools.arxiv import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper, BraveSearchWrapper
from langchain.tools import BaseTool
from typing import Any, Dict, List, Optional, Type

from src.config import SEARCH_MAX_RESULTS, SearchEngine
from src.tools.tavily_search.tavily_search_results_with_images import (
    TavilySearchResultsWithImages,
)

from src.tools.decorators import create_logged_tool

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

LoggedTavilySearch = create_logged_tool(TavilySearchResultsWithImages)
if os.getenv("SEARCH_API", "") == SearchEngine.TAVILY.value:
    tavily_search_tool = LoggedTavilySearch(
        name="web_search",
        max_results=SEARCH_MAX_RESULTS,
        include_raw_content=True,
        include_images=True,
        include_image_descriptions=True,
    )
else:
    tavily_search_tool = None

try:
    logger.debug("Initializing DuckDuckGo search tool...")
    LoggedDuckDuckGoSearch = create_logged_tool(DuckDuckGoSearchResults)
    duckduckgo_search_tool = LoggedDuckDuckGoSearch(
        max_results=SEARCH_MAX_RESULTS
    )
    logger.debug("DuckDuckGo search tool initialized successfully")
except Exception as e:
    logger.error(f"Error initializing DuckDuckGo search tool: {str(e)}", exc_info=True)
    raise

try:
    logger.debug("Initializing Brave search tool...")
    LoggedBraveSearch = create_logged_tool(BraveSearch)
    brave_search_tool = LoggedBraveSearch(
        name="web_search",
        search_wrapper=BraveSearchWrapper(
            api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""),
            search_kwargs={"count": SEARCH_MAX_RESULTS},
        ),
    )
    logger.debug("Brave search tool initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Brave search tool: {str(e)}", exc_info=True)
    raise

try:
    logger.debug("Initializing Arxiv search tool...")
    LoggedArxivSearch = create_logged_tool(ArxivQueryRun)
    arxiv_search_tool = LoggedArxivSearch(
        name="web_search",
        api_wrapper=ArxivAPIWrapper(
            top_k_results=SEARCH_MAX_RESULTS,
            load_max_docs=SEARCH_MAX_RESULTS,
            load_all_available_meta=True,
        ),
    )
    logger.debug("Arxiv search tool initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Arxiv search tool: {str(e)}", exc_info=True)
    raise

if __name__ == "__main__":
    results = LoggedDuckDuckGoSearch(
        name="web_search", max_results=SEARCH_MAX_RESULTS, output_format="list"
    ).invoke("cute panda")
    print(json.dumps(results, indent=2, ensure_ascii=False))
