from ingestion.parse import extract_text_from_html

def test_extract_text_from_html(tmp_path):
    # Test extracting text from a simple HTML file
    html = "<html><body><h1>Title</h1><p>This is a test.</p></body></html>"
    html_file = tmp_path / "test.html"
    html_file.write_text(html, encoding="utf-8")
    text = extract_text_from_html(str(html_file))
    assert "Title" in text
    assert "This is a test." in text

def test_extract_text_from_html_empty(tmp_path):
    # Test extracting text from an empty HTML file
    html_file = tmp_path / "empty.html"
    html_file.write_text("", encoding="utf-8")
    text = extract_text_from_html(str(html_file))
    assert text == "", "Text should be empty for empty HTML file."

def test_extract_text_from_html_malformed(tmp_path):
    # Test extracting text from a malformed HTML file
    html = "<html><body><h1>Unclosed tag"
    html_file = tmp_path / "malformed.html"
    html_file.write_text(html, encoding="utf-8")
    text = extract_text_from_html(str(html_file))
    assert "Unclosed tag" in text

def test_extract_text_from_html_large(tmp_path):
    # Test extracting text from a large HTML file
    html = "<html><body>" + ("<p>Line</p>" * 10000) + "</body></html>"
    html_file = tmp_path / "large.html"
    html_file.write_text(html, encoding="utf-8")
    text = extract_text_from_html(str(html_file))
    assert text.count("Line") == 10000 