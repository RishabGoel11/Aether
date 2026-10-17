from unittest.mock import MagicMock, patch

import pytest

from app.web.search import DuckDuckGoSearch, WebSearchError


def test_search_cleans_uddg_url():
    searcher = DuckDuckGoSearch()
    href = "//duckduckgo.com/l/?uddg=https%3A%2F%2Fpython.org%2Fdownloads&rut=xyz"
    cleaned = searcher._clean_url(href)
    assert cleaned == "https://python.org/downloads"


def test_search_parses_html_results():
    sample_html = """
    <div class="result results_links results_links_deep web-result">
        <h2 class="result__title">
            <a class="result__a" href="https://example.com/one">Example Title One</a>
        </h2>
        <a class="result__snippet">This is the first search snippet.</a>
    </div>
    <div class="result results_links results_links_deep web-result">
        <h2 class="result__title">
            <a class="result__a"
               href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Ftwo">Example Title Two</a>
        </h2>
        <a class="result__snippet">This is the second search snippet.</a>
    </div>
    """

    searcher = DuckDuckGoSearch()
    results = searcher.parse_results(sample_html, max_results=5)

    assert len(results) == 2
    assert results[0].title == "Example Title One"
    assert results[0].url == "https://example.com/one"
    assert results[0].snippet == "This is the first search snippet."
    assert results[1].title == "Example Title Two"
    assert results[1].url == "https://example.com/two"


def test_search_empty_query_returns_empty_list():
    searcher = DuckDuckGoSearch()
    assert searcher.search("") == []
    assert searcher.search("   ") == []


def test_search_handles_http_errors():
    searcher = DuckDuckGoSearch()
    with patch("httpx.Client.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 500")
        mock_post.return_value = mock_response

        with pytest.raises(WebSearchError):
            searcher.search("test query")
