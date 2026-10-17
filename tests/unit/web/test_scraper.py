from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.web.scraper import WebScraper, WebScraperError


def test_scraper_invalid_url_raises():
    scraper = WebScraper()
    with pytest.raises(ValueError, match="Invalid URL schema"):
        scraper.fetch("ftp://example.com/file")


def test_scraper_fetches_and_extracts_page():
    scraper = WebScraper()
    mock_html = (
        "<html><head><title>Test Page</title></head>"
        "<body><p>Hello world from website.</p></body></html>"
    )

    with patch("httpx.Client.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        page = scraper.fetch("https://example.com/test")

        assert page.url == "https://example.com/test"
        assert page.title == "Test Page"
        assert "Hello world from website." in page.text
        assert page.metadata["status_code"] == 200


def test_scraper_handles_timeout():
    scraper = WebScraper()
    with patch("httpx.Client.get", side_effect=httpx.TimeoutException("Timed out")):
        with pytest.raises(WebScraperError, match="Connection timed out"):
            scraper.fetch("https://example.com/slow")


def test_scraper_handles_http_status_error():
    scraper = WebScraper()
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_err = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=mock_response)

    with patch("httpx.Client.get", side_effect=mock_err):
        with pytest.raises(WebScraperError, match="HTTP error 404"):
            scraper.fetch("https://example.com/missing")
