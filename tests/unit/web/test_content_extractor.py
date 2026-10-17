from app.web.extractor import ContentExtractor


def test_extractor_extracts_title_and_meta():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Aether AI Platform</title>
        <meta name="description" content="Local-first AI platform with privacy.">
    </head>
    <body>
        <nav><a href="/">Home</a></nav>
        <main>
            <h1>Welcome</h1>
            <p>Aether is an intelligent modular assistant.</p>
        </main>
        <footer>Copyright 2026</footer>
        <script>console.log("drop me");</script>
    </body>
    </html>
    """

    page = ContentExtractor.extract(html, url="https://example.com/aether")

    assert page.title == "Aether AI Platform"
    assert page.meta_description == "Local-first AI platform with privacy."
    assert "Aether is an intelligent modular assistant." in page.text
    # Check discarded tags
    assert "drop me" not in page.text
    assert "Copyright 2026" not in page.text
    assert "Home" not in page.text


def test_extractor_handles_empty_html():
    page = ContentExtractor.extract("", url="https://example.com")
    assert page.title == ""
    assert page.text == ""


def test_extractor_truncates_long_content():
    html = "<body><p>" + "word " * 500 + "</p></body>"
    page = ContentExtractor.extract(html, max_chars=100)

    assert len(page.text) <= 120
    assert "...[truncated]" in page.text
