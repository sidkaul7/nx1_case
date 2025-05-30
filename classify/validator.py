import json
import re
from typing import List, Dict, Any
from config.config import EventConfig

def extract_json_block(text):
    # Extract the first JSON array or object from the LLM output (handles extra text)
    match = re.search(r'(\[.*?\]|\{.*?\})', text, re.DOTALL)
    if match:
        return match.group(1)
    raise ValueError("Could not find a JSON array or object in the LLM output.")

def validate_zero_shot(result: str, allowed_events: List[str]) -> bool:
    """
    Validate zero-shot classification output.
    
    Args:
        result: Raw model output string
        allowed_events: List of allowed event types
        
    Returns:
        bool: True if validation passes, False otherwise
    """
    try:
        # Try to parse as JSON
        parsed = json.loads(result)
        
        # Check if it's a list
        if not isinstance(parsed, list):
            return False
            
        # Validate each event
        for event in parsed:
            if not isinstance(event, dict):
                return False
                
            if "Event Type" not in event:
                return False
                
            if "Relevant" not in event:
                return False
                
            if event["Event Type"] not in allowed_events:
                return False
                
            if not isinstance(event["Relevant"], bool):
                return False
                
        return True
        
    except json.JSONDecodeError:
        return False

def validate_cot(result: str, allowed_events: List[str]) -> bool:
    """
    Validate chain-of-thought classification output.
    
    Args:
        result: Raw model output string
        allowed_events: List of allowed event types
        
    Returns:
        bool: True if validation passes, False otherwise
    """
    try:
        # Try to parse as JSON
        parsed = json.loads(result)
        
        # Check if it's a dictionary
        if not isinstance(parsed, dict):
            return False
            
        # Check for required fields
        if "Events" not in parsed:
            return False
            
        if "Reasoning" not in parsed:
            return False
            
        # Validate events list
        if not isinstance(parsed["Events"], list):
            return False
            
        # Validate each event
        for event in parsed["Events"]:
            if not isinstance(event, dict):
                return False
                
            if "Event Type" not in event:
                return False
                
            if "Relevant" not in event:
                return False
                
            if event["Event Type"] not in allowed_events:
                return False
                
            if not isinstance(event["Relevant"], bool):
                return False
                
        return True
        
    except json.JSONDecodeError:
        return False

if __name__ == "__main__":
    config = EventConfig()
    allowed_events = config.get_event_types()
    # Quick test: validate a zero-shot output
    zero_shot_output = '[{"Event Type": "Open Market Purchase", "Relevant": true}]'
    print("Zero-shot validation:", validate_zero_shot(zero_shot_output, allowed_events))
    # Quick test: validate a CoT output
    cot_output = '{"Reasoning": ["1. ..."], "Events": [{"Event Type": "Open Market Purchase", "Relevant": true}]}'
    print("CoT validation:", validate_cot(cot_output, allowed_events))
