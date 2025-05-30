import json
import os
import argparse
from classify.llm_client import run_llama3
from config.config import EventConfig
from classify.validator import extract_json_block

def load_prompt(template_name: str) -> str:
    """
    Load a prompt template by name from the prompts directory.
    
    Args:
        template_name: Name of the template (e.g., 'zero_shot.tpl' or 'cot.tpl')
        
    Returns:
        str: The prompt template
    """
    # Map template names to file names
    template_files = {
        "zero_shot.tpl": "zero_shot.tpl",
        "cot.tpl": "cot.tpl"
    }
    
    if template_name not in template_files:
        raise ValueError(f"Unknown template: {template_name}")
    
    # Get the path to the prompts directory
    prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
    template_path = os.path.join(prompts_dir, template_files[template_name])
    
    # Read the template file
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def classify_event(text: str, events: list[str], use_cot: bool = False) -> dict:
    """
    Classify an event using either zero-shot or chain-of-thought prompting.
    
    Args:
        text: The text to classify
        events: List of possible event types
        use_cot: Whether to use chain-of-thought prompting
        
    Returns:
        dict: Classification result with event type and relevance
    """
    # Load appropriate prompt template
    prompt_name = "cot.tpl" if use_cot else "zero_shot.tpl"
    print("Prompt selected:", prompt_name)
    prompt = load_prompt(prompt_name)
    
    # Format prompt with text and events
    formatted_prompt = prompt.format(text=text, events=json.dumps(events))
    # print("==== PROMPT SENT TO MODEL ====")
    # print(formatted_prompt)
    # print("==============================")
    
    # Get LLM response
    response = run_llama3(formatted_prompt)
    
    # Try to parse the response as JSON
    try:
        # First try to parse the entire response
        parsed = json.loads(response)
        return json.dumps(parsed)
    except json.JSONDecodeError:
        # If that fails, try to extract a JSON block
        try:
            json_str = extract_json_block(response)
            parsed = json.loads(json_str)
            return json.dumps(parsed)
        except Exception as e:
            raise ValueError(f"Failed to parse model output as JSON: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Classify events from text")
    parser.add_argument("--text", required=True, help="Text to classify")
    parser.add_argument("--events", required=True, help="JSON array of possible event types")
    parser.add_argument("--use-cot", action="store_true", help="Use chain-of-thought prompting")
    parser.add_argument("--config", help="Path to event configuration file")
    args = parser.parse_args()
    
    try:
        # Use EventConfig to get event types
        config = EventConfig(args.config)
        events = config.get_event_types()
        result = classify_event(args.text, events, args.use_cot)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
