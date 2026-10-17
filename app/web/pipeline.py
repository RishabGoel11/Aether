from __future__ import annotations

from app.llm.base import BaseLLM
from app.llm.models import Message, Role
from app.web.models import WebPageContent, WebResearchReport, WebSearchResult
from app.web.scraper import WebScraper
from app.web.search import BaseWebSearch, DuckDuckGoSearch


class WebPipeline:
    """High-level facade coordinating web search, content scraping, and synthesis."""

    def __init__(
        self,
        search_engine: BaseWebSearch | None = None,
        scraper: WebScraper | None = None,
        llm: BaseLLM | None = None,
    ) -> None:
        self.search_engine = search_engine or DuckDuckGoSearch()
        self.scraper = scraper or WebScraper()
        self.llm = llm

    def search(self, query: str, max_results: int = 5) -> list[WebSearchResult]:
        """Search the internet for query and return structured results."""
        return self.search_engine.search(query, max_results=max_results)

    def scrape(self, url: str, max_chars: int = 15000) -> WebPageContent:
        """Fetch and extract clean text from a web page."""
        return self.scraper.fetch(url, max_chars=max_chars)

    def research(
        self,
        query: str,
        max_sources: int = 3,
        max_chars_per_source: int = 8000,
    ) -> WebResearchReport:
        """Search and scrape top sources into a consolidated research report."""
        search_results = self.search(query, max_results=max_sources)
        pages: list[WebPageContent] = []

        for res in search_results:
            try:
                page = self.scrape(res.url, max_chars=max_chars_per_source)
                if not page.title:
                    page.title = res.title
                pages.append(page)
            except Exception:
                # If a specific page fails to fetch, keep going with other sources
                continue

        # If LLM is available, generate a synthesis
        summary = ""
        if self.llm and pages:
            summary = self._synthesize(query, pages)
        elif pages:
            summary = f"Gathered {len(pages)} source pages for query: '{query}'."

        return WebResearchReport(
            query=query,
            sources=pages,
            summary=summary,
        )

    def _synthesize(self, query: str, pages: list[WebPageContent]) -> str:
        """Use LLM to synthesize research findings across scraped sources."""
        context_parts: list[str] = []
        for i, page in enumerate(pages):
            header = f"--- Source {i + 1}: {page.title} ({page.url}) ---"
            snippet = page.text[:3000]
            context_parts.append(f"{header}\n{snippet}")

        context = "\n\n".join(context_parts)
        prompt = (
            f"Based on the following web sources, provide a clear, accurate, and concise answer "
            f"to the user query.\n\n"
            f"Query: {query}\n\n"
            f"Web Sources:\n{context}\n\n"
            f"Answer:"
        )

        messages = [
            Message(
                role=Role.SYSTEM,
                content=(
                    "You are an expert research assistant grounding your answers "
                    "in provided web sources."
                ),
            ),
            Message(role=Role.USER, content=prompt),
        ]

        try:
            response = self.llm.generate(messages)
            return response.content.strip()
        except Exception as exc:
            return f"Error synthesizing research report: {exc}"
