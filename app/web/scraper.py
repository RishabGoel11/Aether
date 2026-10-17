from __future__ import annotations

import httpx

from app.web.extractor import ContentExtractor
from app.web.models import WebPageContent

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 Aether/0.8.0"
)


class WebScraperError(Exception):
    """Raised when web scraping fails."""


class WebScraper:
    """Fetches and extracts clean content from web pages."""

    def __init__(self, user_agent: str = DEFAULT_USER_AGENT, timeout: float = 10.0) -> None:
        self.user_agent = user_agent
        self.timeout = timeout

    def fetch(
        self,
        url: str,
        timeout: float | None = None,
        max_chars: int = 20000,
    ) -> WebPageContent:
        """Fetch a URL over HTTP/HTTPS and return cleaned content."""
        if not (url.startswith("http://") or url.startswith("https://")):
            raise ValueError(f"Invalid URL schema (must begin with http:// or https://): '{url}'")

        effective_timeout = timeout if timeout is not None else self.timeout

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        try:
            with httpx.Client(
                headers=headers,
                timeout=effective_timeout,
                follow_redirects=True,
            ) as client:
                response = client.get(url)
                response.raise_for_status()
                html = response.text

        except httpx.HTTPStatusError as exc:
            raise WebScraperError(
                f"HTTP error {exc.response.status_code} fetching URL: {url}"
            ) from exc
        except httpx.TimeoutException as exc:
            raise WebScraperError(
                f"Connection timed out after {effective_timeout}s fetching URL: {url}"
            ) from exc
        except httpx.RequestError as exc:
            raise WebScraperError(f"Network error fetching URL '{url}': {exc}") from exc

        page = ContentExtractor.extract(html=html, url=url, max_chars=max_chars)
        page.metadata["status_code"] = response.status_code
        return page
