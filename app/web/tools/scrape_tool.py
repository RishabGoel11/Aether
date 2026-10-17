from __future__ import annotations

from pydantic import BaseModel, Field

from app.tools.base import BaseTool
from app.tools.models import ToolResult
from app.web.scraper import WebScraper, WebScraperError


class WebScrapeArgs(BaseModel):
    """Arguments accepted by the web scraper tool."""

    url: str = Field(
        min_length=1,
        description="URL of the webpage to fetch and read (must begin with http:// or https://).",
    )
    max_chars: int = Field(
        default=10000,
        ge=500,
        le=50000,
        description="Maximum characters of cleaned text to extract.",
    )


class WebScrapeTool(BaseTool[WebScrapeArgs]):
    """Fetch and extract clean readable text content from a web URL."""

    name = "web_scrape"
    description = (
        "Fetch and read the text content of a web page URL. "
        "Strips out HTML tags, navigation, footers, scripts, and ads to return clean text."
    )
    args_schema = WebScrapeArgs

    def __init__(self, scraper: WebScraper | None = None) -> None:
        self.scraper = scraper or WebScraper()

    def execute(self, args: WebScrapeArgs) -> ToolResult:
        try:
            page = self.scraper.fetch(url=args.url, max_chars=args.max_chars)

            output = {
                "url": page.url,
                "title": page.title,
                "meta_description": page.meta_description,
                "content": page.text,
                "char_count": len(page.text),
            }

            return ToolResult(
                success=True,
                output=output,
            )

        except (WebScraperError, ValueError) as exc:
            return ToolResult(
                success=False,
                error=f"Web scrape failed: {exc}",
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"Unexpected error scraping webpage '{args.url}': {exc}",
            )
