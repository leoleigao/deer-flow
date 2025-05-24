# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import pytest
from src.crawler import Crawler
from src.crawler.jina_client import JinaClient


def test_crawler_initialization():
    """Test that crawler can be properly initialized."""
    crawler = Crawler()
    assert isinstance(crawler, Crawler)


def test_crawler_crawl_valid_url(monkeypatch):
    """Test crawling with a valid URL."""
    crawler = Crawler()

    def stub_crawl(self, url, return_format="html"):
        return "<html><body><p>Stub</p></body></html>"

    monkeypatch.setattr(JinaClient, "crawl", stub_crawl)
    test_url = "https://example.com"
    result = crawler.crawl(test_url)
    assert result is not None
    assert hasattr(result, "to_markdown")


def test_crawler_markdown_output(monkeypatch):
    """Test that crawler output can be converted to markdown."""
    crawler = Crawler()

    def stub_crawl(self, url, return_format="html"):
        return "<html><body><p>Stub</p></body></html>"

    monkeypatch.setattr(JinaClient, "crawl", stub_crawl)
    test_url = "https://example.com"
    result = crawler.crawl(test_url)
    markdown = result.to_markdown()
    assert isinstance(markdown, str)
    assert len(markdown) > 0
