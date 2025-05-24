# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import os

try:
    import requests
except Exception:  # pragma: no cover - requests missing in minimal env
    requests = None

logger = logging.getLogger(__name__)


class JinaClient:
    def crawl(self, url: str, return_format: str = "html") -> str:
        headers = {
            "Content-Type": "application/json",
            "X-Return-Format": return_format,
        }
        if os.getenv("JINA_API_KEY"):
            headers["Authorization"] = f"Bearer {os.getenv('JINA_API_KEY')}"
        else:
            logger.warning(
                "Jina API key is not set. Provide your own key to access a higher rate limit. See https://jina.ai/reader for more information."
            )
        if requests is None:
            logger.warning("requests not available; returning stub content")
            return f"<html><body><p>Stub content for {url}</p></body></html>"

        data = {"url": url}
        try:
            response = requests.post("https://r.jina.ai/", headers=headers, json=data)
            response.raise_for_status()
            return response.text
        except Exception as e:  # pragma: no cover - network issues
            logger.error("Failed to crawl %s: %s", url, e)
            return f"<html><body><p>Stub content for {url}</p></body></html>"
