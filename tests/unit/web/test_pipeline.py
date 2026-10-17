from unittest.mock import MagicMock

from app.llm.base import BaseLLM
from app.llm.models import LLMResponse
from app.web.models import WebPageContent, WebSearchResult
from app.web.pipeline import WebPipeline
from app.web.scraper import WebScraper
from app.web.search import BaseWebSearch


def test_web_pipeline_search_and_scrape():
    mock_searcher = MagicMock(spec=BaseWebSearch)
    mock_searcher.search.return_value = [
        WebSearchResult(title="Result 1", url="https://example.com/1", snippet="Snippet 1")
    ]
    mock_scraper = MagicMock(spec=WebScraper)
    mock_scraper.fetch.return_value = WebPageContent(
        url="https://example.com/1",
        title="Result 1",
        text="Full text from page 1.",
    )

    pipeline = WebPipeline(search_engine=mock_searcher, scraper=mock_scraper)

    search_res = pipeline.search("test")
    assert len(search_res) == 1

    page = pipeline.scrape("https://example.com/1")
    assert page.text == "Full text from page 1."


def test_web_pipeline_research_with_llm():
    mock_searcher = MagicMock(spec=BaseWebSearch)
    mock_searcher.search.return_value = [
        WebSearchResult(title="Page A", url="https://example.com/a", snippet="Snippet A")
    ]
    mock_scraper = MagicMock(spec=WebScraper)
    mock_scraper.fetch.return_value = WebPageContent(
        url="https://example.com/a",
        title="Page A",
        text="Detailed text about topic A.",
    )
    mock_llm = MagicMock(spec=BaseLLM)
    mock_llm.generate.return_value = LLMResponse(content="Topic A is deeply interesting.")

    pipeline = WebPipeline(
        search_engine=mock_searcher,
        scraper=mock_scraper,
        llm=mock_llm,
    )

    report = pipeline.research("learn topic A", max_sources=1)

    assert report.query == "learn topic A"
    assert len(report.sources) == 1
    assert report.summary == "Topic A is deeply interesting."
