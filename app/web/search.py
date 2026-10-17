from __future__ import annotations

import urllib.parse
from abc import ABC, abstractmethod

import httpx
from bs4 import BeautifulSoup

from app.web.models import WebSearchResult

DEFAULT_SEARCH_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 Aether/0.8.0"
)


class WebSearchError(Exception):
    """Raised when web search fails."""


class BaseWebSearch(ABC):
    """Abstract interface for web search engines."""

    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> list[WebSearchResult]:
        """Perform a web search and return structured results."""


class DuckDuckGoSearch(BaseWebSearch):
    """Zero-API-key search engine using DuckDuckGo HTML service."""

    SEARCH_URL = "https://html.duckduckgo.com/html/"

    def __init__(
        self,
        user_agent: str = DEFAULT_SEARCH_USER_AGENT,
        timeout: float = 10.0,
    ) -> None:
        self.user_agent = user_agent
        self.timeout = timeout

    def _clean_url(self, href: str) -> str:
        """Decode DuckDuckGo redirect link to extract destination URL."""
        if not href:
            return ""
        if "uddg=" in href:
            parsed = urllib.parse.urlparse(href)
            qs = urllib.parse.parse_qs(parsed.query)
            extracted = qs.get("uddg")
            if extracted:
                return urllib.parse.unquote(extracted[0])
        return href

    def search(self, query: str, max_results: int = 5) -> list[WebSearchResult]:
        clean_query = query.strip()
        if not clean_query:
            return []

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            with httpx.Client(
                headers=headers,
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                response = client.post(
                    self.SEARCH_URL,
                    data={"q": clean_query},
                )
                response.raise_for_status()
                html = response.text

        except httpx.HTTPStatusError as exc:
            raise WebSearchError(
                f"HTTP error {exc.response.status_code} during search: {exc}"
            ) from exc
        except httpx.TimeoutException as exc:
            raise WebSearchError(
                f"Web search timed out after {self.timeout}s for query: '{query}'"
            ) from exc
        except httpx.RequestError as exc:
            raise WebSearchError(f"Network error during web search: {exc}") from exc
        except Exception as exc:
            raise WebSearchError(f"Error executing web search for '{clean_query}': {exc}") from exc

        return self.parse_results(html, max_results=max_results)

    def parse_results(self, html: str, max_results: int = 5) -> list[WebSearchResult]:
        """Parse DuckDuckGo HTML markup into structured WebSearchResult models."""
        soup = BeautifulSoup(html, "html.parser")
        results: list[WebSearchResult] = []

        result_divs = soup.find_all("div", class_="result")
        for div in result_divs:
            if len(results) >= max_results:
                break

            # Look for main title link
            title_tag = div.find("a", class_="result__a")
            if not title_tag:
                continue

            raw_title = title_tag.get_text(strip=True)
            raw_href = str(title_tag.get("href", ""))
            clean_url = self._clean_url(raw_href)

            if not raw_title or not clean_url:
                continue

            # Look for snippet
            snippet = ""
            if snippet_tag := div.find("a", class_="result__snippet"):
                snippet = snippet_tag.get_text(strip=True)

            results.append(
                WebSearchResult(
                    title=raw_title,
                    url=clean_url,
                    snippet=snippet,
                )
            )

        return results
