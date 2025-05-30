from ingestion.ingest import download_8k

def test_download_8k(tmp_path):
    # Test downloading a valid SEC 8-K filing and checking file content
    url = "https://www.sec.gov/Archives/edgar/data/320193/000119312521328151/d259993d8k.htm"
    output_path = tmp_path / "d259993d8k.htm"
    download_8k(url, str(output_path))
    assert output_path.exists(), "Downloaded file does not exist."
    content = output_path.read_text(encoding='utf-8')
    assert "8-K" in content or "UNITED STATES SECURITIES AND EXCHANGE COMMISSION" in content, "Downloaded file does not appear to be a valid SEC filing."

def test_download_8k_invalid_url(tmp_path):
    # Test that an invalid URL does not create a file
    url = "https://www.sec.gov/Archives/edgar/data/320193/00000000000000000000000000000000/invalid.htm"
    output_path = tmp_path / "invalid.htm"
    download_8k(url, str(output_path))
    assert not output_path.exists(), "File should not exist for invalid URL."

def test_download_8k_overwrite(tmp_path):
    # Test that downloading overwrites an existing file
    url = "https://www.sec.gov/Archives/edgar/data/320193/000119312521328151/d259993d8k.htm"
    output_path = tmp_path / "d259993d8k.htm"
    output_path.write_text("old content", encoding="utf-8")
    download_8k(url, str(output_path))
    content = output_path.read_text(encoding='utf-8')
    assert "old content" not in content, "File was not overwritten as expected." 