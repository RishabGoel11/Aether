from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.rag.models import Document


class BaseDocumentLoader(ABC):
    """Abstract interface for loading documents."""

    @abstractmethod
    def load(self, path: str | Path) -> Document:
        """Load a file into a Document."""


class TextLoader(BaseDocumentLoader):
    """Loads plain text files."""

    def load(self, path: str | Path) -> Document:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        content = file_path.read_text(encoding="utf-8")
        return Document(
            source=str(file_path),
            content=content,
            metadata={"filename": file_path.name, "extension": file_path.suffix},
        )


class MarkdownLoader(BaseDocumentLoader):
    """Loads Markdown files."""

    def load(self, path: str | Path) -> Document:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        content = file_path.read_text(encoding="utf-8")
        return Document(
            source=str(file_path),
            content=content,
            metadata={
                "filename": file_path.name,
                "extension": file_path.suffix,
                "format": "markdown",
            },
        )


class PDFLoader(BaseDocumentLoader):
    """Loads PDF documents extracting text page-by-page."""

    def load(self, path: str | Path) -> Document:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        from pypdf import PdfReader
        from pypdf.errors import PdfReadError

        try:
            reader = PdfReader(str(file_path))
        except PdfReadError as exc:
            raise ValueError(f"Invalid or corrupted PDF file: {exc}") from exc

        if reader.is_encrypted:
            try:
                decrypted = reader.decrypt("")
                if decrypted == 0:
                    raise ValueError(f"PDF file is password protected: {file_path.name}")
            except Exception as exc:
                raise ValueError(f"Unable to decrypt PDF: {exc}") from exc

        page_texts: list[str] = []
        for page_idx, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()
            if text:
                page_texts.append(f"--- Page {page_idx + 1} ---\n{text}")

        total_pages = len(reader.pages)
        content = "\n\n".join(page_texts)

        return Document(
            source=str(file_path),
            content=content,
            metadata={
                "filename": file_path.name,
                "extension": file_path.suffix,
                "format": "pdf",
                "page_count": total_pages,
            },
        )


class DocumentLoaderFactory:
    """Factory to get the appropriate loader by file extension."""

    LOADERS: dict[str, type[BaseDocumentLoader]] = {
        ".txt": TextLoader,
        ".md": MarkdownLoader,
        ".markdown": MarkdownLoader,
        ".pdf": PDFLoader,
    }

    @classmethod
    def get_loader(cls, path: str | Path) -> BaseDocumentLoader:
        file_path = Path(path)
        ext = file_path.suffix.lower()
        loader_cls = cls.LOADERS.get(ext)
        if loader_cls is None:
            raise ValueError(
                f"Unsupported file type: '{ext}'. Supported types: {list(cls.LOADERS.keys())}"
            )
        return loader_cls()

    @classmethod
    def load(cls, path: str | Path) -> Document:
        loader = cls.get_loader(path)
        return loader.load(path)

    @classmethod
    def load_directory(
        cls,
        dir_path: str | Path,
        recursive: bool = True,
    ) -> list[Document]:
        directory = Path(dir_path)
        if not directory.exists() or not directory.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory}")

        documents: list[Document] = []
        pattern = "**/*" if recursive else "*"
        for item in directory.glob(pattern):
            if item.is_file() and item.suffix.lower() in cls.LOADERS:
                try:
                    loader = cls.get_loader(item)
                    documents.append(loader.load(item))
                except Exception:
                    continue

        return documents
