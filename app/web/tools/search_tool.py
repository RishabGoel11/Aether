from __future__ import annotations

from pydantic import BaseModel, Field

from app.tools.base import BaseTool
from app.tools.models import ToolResult
from app.web.search import BaseWebSearch, DuckDuckGoSearch, WebSearchError


class WebSearchArgs(BaseModel):
    """Arguments accepted by the web search tool."""

    query: str = Field(
        min_length=1,
        description="Search query to look up on the web.",
    )
    max_results: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of search results to retrieve.",
    )


class WebSearchTool(BaseTool[WebSearchArgs]):
    """Search the internet for current information, documentation, and facts."""

    name = "web_search"
    description = (
        "Search the internet for up-to-date information, news, documentation, or facts. "
        "Returns titles, URLs, and summary snippets."
    )
    args_schema = WebSearchArgs

    def __init__(self, search_engine: BaseWebSearch | None = None) -> None:
        self.search_engine = search_engine or DuckDuckGoSearch()

    def execute(self, args: WebSearchArgs) -> ToolResult:
        try:
            results = self.search_engine.search(
                query=args.query,
                max_results=args.max_results,
            )

            if not results:
                return ToolResult(
                    success=True,
                    output=f"No web results found for query: '{args.query}'",
                )

            formatted_results: list[dict[str, str]] = [
                {
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.snippet,
                }
                for r in results
            ]

            return ToolResult(
                success=True,
                output=formatted_results,
            )

        except WebSearchError as exc:
            return ToolResult(
                success=False,
                error=f"Web search failed: {exc}",
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"Unexpected error executing web search: {exc}",
            )
