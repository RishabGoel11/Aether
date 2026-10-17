from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class WebSearchResult(BaseModel):
    """Represents a single search result from a web search engine."""

    title: str = Field(description="Title of the search result page.")
    url: str = Field(description="URL link to the webpage.")
    snippet: str = Field(description="Extracted summary snippet from the search engine.")


class WebPageContent(BaseModel):
    """Represents extracted, clean text content from a fetched webpage."""

    url: str = Field(description="The source URL of the page.")
    title: str = Field(default="", description="The extracted title of the page.")
    text: str = Field(description="Cleaned, human-readable text extracted from the page.")
    meta_description: str = Field(
        default="",
        description="Meta description of the webpage if available.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional page metadata (e.g. status code, char count, etc.).",
    )


class WebResearchReport(BaseModel):
    """Consolidated web research report across multiple sources."""

    query: str = Field(description="The original search query.")
    sources: list[WebPageContent] = Field(
        default_factory=list,
        description="Pages successfully scraped for this report.",
    )
    summary: str = Field(
        default="",
        description="Synthesized summary or answer based on the retrieved sources.",
    )
