from unittest.mock import MagicMock

from app.web.models import WebPageContent, WebSearchResult
from app.web.scraper import WebScraper
from app.web.search import BaseWebSearch
from app.web.tools import WebScrapeArgs, WebScrapeTool, WebSearchArgs, WebSearchTool


def test_web_search_tool_executes_successfully():
    mock_searcher = MagicMock(spec=BaseWebSearch)
    mock_searcher.search.return_value = [
        WebSearchResult(
            title="Aether Docs",
            url="https://github.com/RishabGoel11/Aether",
            snippet="Modular local AI platform.",
        )
    ]

    tool = WebSearchTool(search_engine=mock_searcher)
    result = tool.execute(WebSearchArgs(query="Aether AI", max_results=2))

    assert result.success is True
    assert isinstance(result.output, list)
    assert len(result.output) == 1
    assert result.output[0]["title"] == "Aether Docs"


def test_web_search_tool_handles_empty_results():
    mock_searcher = MagicMock(spec=BaseWebSearch)
    mock_searcher.search.return_value = []

    tool = WebSearchTool(search_engine=mock_searcher)
    result = tool.execute(WebSearchArgs(query="nonexistent term"))

    assert result.success is True
    assert "No web results found" in str(result.output)


def test_web_scrape_tool_executes_successfully():
    mock_scraper = MagicMock(spec=WebScraper)
    mock_scraper.fetch.return_value = WebPageContent(
        url="https://example.com/guide",
        title="Guide Title",
        text="Clean page content for testing.",
        meta_description="A sample guide.",
    )

    tool = WebScrapeTool(scraper=mock_scraper)
    result = tool.execute(WebScrapeArgs(url="https://example.com/guide"))

    assert result.success is True
    assert result.output["title"] == "Guide Title"
    assert "Clean page content" in result.output["content"]


def test_web_scrape_tool_handles_error():
    mock_scraper = MagicMock(spec=WebScraper)
    mock_scraper.fetch.side_effect = ValueError("Invalid URL schema")

    tool = WebScrapeTool(scraper=mock_scraper)
    result = tool.execute(WebScrapeArgs(url="bad-url"))

    assert result.success is False
    assert "Web scrape failed" in result.error
