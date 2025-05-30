import os

PROMPT_DIR = os.path.join(os.path.dirname(__file__), '..', 'prompts')

def build_prompt(template_name, text, events):
    """
    Loads a prompt template and fills in the SEC filing text and event list.
    """
    template_path = os.path.join(PROMPT_DIR, template_name)
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    # Join event names as a quoted, comma-separated list for the prompt
    events_str = ', '.join(f'"{e}"' for e in events)
    prompt = template.replace('{text}', text).replace('{events}', events_str)
    return prompt

if __name__ == "__main__":
    # Quick test: build both prompt types for a CEO stock purchase event
    filing_text = "The CEO purchased 10,000 shares of Apple stock on the open market."
    events = ["Open Market Purchase", "Open Market Sale", "Option Exercise"]
    print(build_prompt('zero_shot.tpl', filing_text, events))
    print('\n---\n')
    print(build_prompt('cot.tpl', filing_text, events))
