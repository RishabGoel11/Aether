from pathlib import Path

import pytest

from app.rag.loader import (
    DocumentLoaderFactory,
    MarkdownLoader,
    TextLoader,
)


def test_text_loader_reads_file(tmp_path: Path):
    file = tmp_path / "hello.txt"
    file.write_text("Hello Aether RAG", encoding="utf-8")

    loader = TextLoader()
    doc = loader.load(file)

    assert doc.content == "Hello Aether RAG"
    assert doc.metadata["filename"] == "hello.txt"
    assert doc.metadata["extension"] == ".txt"


def test_markdown_loader_reads_file(tmp_path: Path):
    file = tmp_path / "guide.md"
    file.write_text("# Guide\nThis is markdown.", encoding="utf-8")

    loader = MarkdownLoader()
    doc = loader.load(file)

    assert doc.content == "# Guide\nThis is markdown."
    assert doc.metadata["format"] == "markdown"


def test_loader_missing_file_raises(tmp_path: Path):
    missing = tmp_path / "nonexistent.txt"
    loader = TextLoader()
    with pytest.raises(FileNotFoundError):
        loader.load(missing)


def test_factory_dispatches_correct_loader(tmp_path: Path):
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Text", encoding="utf-8")

    md_file = tmp_path / "test.md"
    md_file.write_text("# MD", encoding="utf-8")

    doc_txt = DocumentLoaderFactory.load(txt_file)
    doc_md = DocumentLoaderFactory.load(md_file)

    assert doc_txt.content == "Text"
    assert doc_md.content == "# MD"


def test_factory_unsupported_extension_raises(tmp_path: Path):
    pdf_file = tmp_path / "test.pdf"
    with pytest.raises(ValueError, match="Unsupported file type"):
        DocumentLoaderFactory.get_loader(pdf_file)


def test_factory_load_directory(tmp_path: Path):
    sub = tmp_path / "nested"
    sub.mkdir()

    (tmp_path / "doc1.txt").write_text("Doc 1", encoding="utf-8")
    (sub / "doc2.md").write_text("Doc 2", encoding="utf-8")
    (sub / "ignore.bin").write_bytes(b"\x00\x01")

    docs = DocumentLoaderFactory.load_directory(tmp_path, recursive=True)
    assert len(docs) == 2
    contents = {d.content for d in docs}
    assert contents == {"Doc 1", "Doc 2"}


def test_factory_load_directory_non_recursive(tmp_path: Path):
    sub = tmp_path / "nested"
    sub.mkdir()

    (tmp_path / "doc1.txt").write_text("Doc 1", encoding="utf-8")
    (sub / "doc2.md").write_text("Doc 2", encoding="utf-8")

    docs = DocumentLoaderFactory.load_directory(tmp_path, recursive=False)
    assert len(docs) == 1
    assert docs[0].content == "Doc 1"
