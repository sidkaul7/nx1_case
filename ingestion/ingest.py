import os
import requests
import time
from urllib.parse import unquote

def download_8k(url: str, output_path: str) -> None:
    """
    Download an 8-K filing from SEC EDGAR.
    
    Args:
        url: URL of the 8-K filing
        output_path: Path to save the downloaded file
    """
    # Clean up the URL and filename
    url = unquote(url)  # Decode URL-encoded characters
    filename = os.path.basename(url).strip()  # Remove any whitespace
    
    # SEC EDGAR requires specific headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; SEC-CaseStudyBot/1.0; +https://yourdomain.com)',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }
    
    try:
        # SEC requires 10 requests per second limit
        time.sleep(0.1)  # Add a small delay to respect rate limits
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"Failed to download filing (status {getattr(e.response, 'status_code', 'unknown')}): {url}")
        raise
