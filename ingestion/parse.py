from bs4 import BeautifulSoup

def extract_text_from_html(html_path):
    """
    Extracts plain text from an HTML SEC filing. Returns the text as a string.
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n").strip()

if __name__ == "__main__":
    # Quick test: print the first 1000 characters of a parsed Apple 8-K
    html_path = "data/filings/d259993d8k.htm"
    text = extract_text_from_html(html_path)
    print(text[:1000])
