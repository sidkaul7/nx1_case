from classify.build_prompt import build_prompt
import pytest

def test_build_prompt():
    # Test building a prompt with a normal event list and filing text
    filing_text = "Sample event text."
    events = ["Acquisition", "Other"]
    prompt = build_prompt("zero_shot.tpl", filing_text, events)
    assert isinstance(prompt, str)
    assert "Sample event text." in prompt
    assert "Acquisition" in prompt

def test_build_prompt_invalid_template():
    # Test building a prompt with an invalid template name (should raise Exception)
    filing_text = "Sample event text."
    events = ["Acquisition", "Other"]
    with pytest.raises(Exception):
        build_prompt("nonexistent.tpl", filing_text, events)

def test_build_prompt_empty_events():
    # Test building a prompt with an empty event list
    filing_text = "Sample event text."
    events = []
    prompt = build_prompt("zero_shot.tpl", filing_text, events)
    assert isinstance(prompt, str)
    assert "Sample event text." in prompt

def test_build_prompt_long_event_list():
    # Test building a prompt with a long event list
    filing_text = "Sample event text."
    events = [f"Event{i}" for i in range(100)]
    prompt = build_prompt("zero_shot.tpl", filing_text, events)
    assert isinstance(prompt, str)
    assert "Event99" in prompt

def test_build_prompt_diverse_companies():
    companies = [
        ("Apple announced the acquisition of a major AI startup.", "Acquisition"),
        ("Google's CFO will retire at the end of the quarter.", "Personnel Change"),
        ("Coca-Cola acquired a minority stake in a beverage startup.", "Acquisition"),
        ("Delta Airlines signed a long-term contract with Boeing for new aircraft.", "Customer Event"),
        ("ExxonMobil reported a quarterly loss due to falling oil prices.", "Financial Event"),
        ("A director at Ford sold 1,500 shares in an open market transaction.", "Open Market Sale"),
    ]
    events = ["Acquisition", "Customer Event", "Personnel Change", "Financial Event", "Open Market Purchase", "Open Market Sale", "Option Exercise", "Shares Withheld for Taxes", "Automatic Sale under Rule 10b5-1", "Other"]
    for filing_text, event in companies:
        prompt_zero = build_prompt("zero_shot.tpl", filing_text, events)
        assert isinstance(prompt_zero, str)
        assert filing_text in prompt_zero
        assert event in prompt_zero
        prompt_cot = build_prompt("cot.tpl", filing_text, events)
        assert isinstance(prompt_cot, str)
        assert filing_text in prompt_cot
        assert event in prompt_cot 