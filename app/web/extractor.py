from __future__ import annotations

import re

from bs4 import BeautifulSoup

from app.web.models import WebPageContent

DISCARD_TAGS = {
    "script",
    "style",
    "noscript",
    "header",
    "footer",
    "nav",
    "aside",
    "iframe",
    "svg",
    "button",
    "form",
    "select",
    "textarea",
}


class ContentExtractor:
    """Extracts clean, readable markdown-like text from raw HTML markup."""

    @classmethod
    def extract(
        cls,
        html: str,
        url: str = "",
        max_chars: int = 20000,
    ) -> WebPageContent:
        """Parse HTML string and extract clean text and metadata."""
        if not html or not html.strip():
            return WebPageContent(url=url, title="", text="", metadata={"char_count": 0})

        soup = BeautifulSoup(html, "html.parser")

        # 1. Extract Title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif og_title := soup.find("meta", property="og:title"):
            title = str(og_title.get("content", "")).strip()

        # 2. Extract Meta Description
        meta_desc = ""
        if meta_tag := soup.find("meta", attrs={"name": "description"}):
            meta_desc = str(meta_tag.get("content", "")).strip()
        elif og_desc := soup.find("meta", property="og:description"):
            meta_desc = str(og_desc.get("content", "")).strip()

        # 3. Discard boilerplate and interactive elements
        for tag_name in DISCARD_TAGS:
            for el in soup.find_all(tag_name):
                el.decompose()

        # 4. Target primary content container if available
        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_=re.compile(r"content|post|article|body", re.I))
            or soup.body
            or soup
        )

        # 5. Extract text with paragraph spacing
        raw_text = main_content.get_text(separator="\n")

        # Clean excessive whitespace and empty lines
        lines = [line.strip() for line in raw_text.splitlines()]
        cleaned_text = "\n".join(line for line in lines if line)

        # Enforce max_chars limit
        if len(cleaned_text) > max_chars:
            cleaned_text = cleaned_text[:max_chars].rstrip() + "\n...[truncated]"

        return WebPageContent(
            url=url,
            title=title,
            text=cleaned_text,
            meta_description=meta_desc,
            metadata={
                "char_count": len(cleaned_text),
                "original_char_count": len(raw_text),
            },
        )
