import pytest
from classify.validator import validate_zero_shot, validate_cot

def test_validate_zero_shot():
    # Test validate_zero_shot with valid and invalid event outputs
    allowed_events = ["Acquisition", "Other"]
    valid_output = '[{"Event Type": "Acquisition", "Relevant": true}]'
    invalid_output = '[{"Event Type": "Unknown", "Relevant": true}]'
    assert validate_zero_shot(valid_output, allowed_events) is True
    assert validate_zero_shot(invalid_output, allowed_events) is False

def test_validate_zero_shot_missing_fields():
    # Test validate_zero_shot with missing required fields
    allowed_events = ["Acquisition", "Other"]
    missing_event_type = '[{"Relevant": true}]'
    missing_relevant = '[{"Event Type": "Acquisition"}]'
    assert validate_zero_shot(missing_event_type, allowed_events) is False
    assert validate_zero_shot(missing_relevant, allowed_events) is False

def test_validate_zero_shot_extra_fields():
    # Test validate_zero_shot with extra fields in output (should still pass)
    allowed_events = ["Acquisition", "Other"]
    extra_fields_output = '[{"Event Type": "Acquisition", "Relevant": true, "extra": 123}]'
    assert validate_zero_shot(extra_fields_output, allowed_events) is True

def test_validate_zero_shot_malformed():
    # Test validate_zero_shot with malformed JSON output
    allowed_events = ["Acquisition", "Other"]
    malformed_output = '[{"Event Type": "Acquisition", "Relevant": true'
    assert validate_zero_shot(malformed_output, allowed_events) is False

def test_validate_cot():
    # Test validate_cot with valid and invalid event outputs
    allowed_events = ["Acquisition", "Other"]
    valid_output = '{"Reasoning": ["Reasoning here"], "Events": [{"Event Type": "Acquisition", "Relevant": true}]}'
    invalid_output = '{"Reasoning": ["Reasoning here"], "Events": [{"Event Type": "Unknown", "Relevant": true}]}'
    assert validate_cot(valid_output, allowed_events) is True
    assert validate_cot(invalid_output, allowed_events) is False

def test_validate_cot_missing_fields():
    # Test validate_cot with missing required fields
    allowed_events = ["Acquisition", "Other"]
    missing_reasoning = '{"Events": [{"Event Type": "Acquisition", "Relevant": true}]}'
    missing_events = '{"Reasoning": ["Reasoning here"]}'
    assert validate_cot(missing_reasoning, allowed_events) is False
    assert validate_cot(missing_events, allowed_events) is False

def test_validate_cot_extra_fields():
    # Test validate_cot with extra fields in output (should still pass)
    allowed_events = ["Acquisition", "Other"]
    extra_fields_output = '{"Reasoning": ["Reasoning here"], "Events": [{"Event Type": "Acquisition", "Relevant": true}], "extra": 123}'
    assert validate_cot(extra_fields_output, allowed_events) is True

def test_validate_cot_malformed():
    # Test validate_cot with malformed JSON output
    allowed_events = ["Acquisition", "Other"]
    malformed_output = '{"Reasoning": ["Reasoning here"], "Events": [{"Event Type": "Acquisition"}'
    assert validate_cot(malformed_output, allowed_events) is False 