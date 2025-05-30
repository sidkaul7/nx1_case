import os
import sys
import argparse
import json
import uuid
from ingestion.ingest import download_8k
from ingestion.parse import extract_text_from_html
from classify.classify import classify_event
from classify.validator import validate_zero_shot, validate_cot
from data.db import insert_result
from config.config import EventConfig

DATA_DIR = "data/filings"
GROUND_TRUTH_PATH = "config/ground_truth.json"
OUTPUTS_DIR = "outputs"

def eval_ground_truth(template, config_path=None, store_in_db=False):
    """Evaluate against ground truth examples."""
    print(f"\nStarting ground truth evaluation using {template} template...")
    with open(GROUND_TRUTH_PATH) as f:
        examples = json.load(f)
    print(f"Loaded {len(examples)} examples from ground truth.")
    results = {}
    config = EventConfig(config_path)
    allowed_events = config.get_event_types()
    
    # Initialize metrics
    total = len(examples)
    correct_event = 0
    correct_relevance = 0
    confusion_matrix = {event: {event: 0 for event in allowed_events} for event in allowed_events}
    
    for i, ex in enumerate(examples, 1):
        print(f"\nProcessing example {i}/{len(examples)}...")
        print(f"Text: {ex['text'][:100]}...")  # Print first 100 chars of text
        result = classify_event(ex['text'], allowed_events, template == 'cot.tpl')
        # Try to parse model output as JSON
        try:
            parsed_output = json.loads(result)
        except Exception:
            parsed_output = result
        # Generate a unique ID for this evaluation run
        req_id = f"{ex.get('filing_id', 'unknown')}_{str(uuid.uuid4())[:8]}"
        
        # Validate the output
        if template == 'zero_shot.tpl':
            validation = validate_zero_shot(result, allowed_events)
        else:
            validation = validate_cot(result, allowed_events)
            
        print(f"Model output: {result}")
        print(f"Validation: {validation}")
        
        # Get predicted event and relevance
        if template == 'zero_shot.tpl':
            predicted_event = parsed_output[0]['Event Type'] if parsed_output else None
            predicted_relevance = parsed_output[0]['Relevant'] if parsed_output else None
        else:
            predicted_event = parsed_output['Events'][0]['Event Type'] if parsed_output.get('Events') else None
            predicted_relevance = parsed_output['Events'][0]['Relevant'] if parsed_output.get('Events') else None
            
        # Update metrics
        if predicted_event == ex['expected_event']:
            correct_event += 1
        if predicted_relevance == ex['expected_relevance']:
            correct_relevance += 1
            
        # Update confusion matrix
        if predicted_event and ex['expected_event']:
            confusion_matrix[ex['expected_event']][predicted_event] += 1
            
        results[req_id] = {
            'id': req_id,
            'text': ex['text'],
            'model_output': parsed_output,
            'expected_event': ex['expected_event'],
            'expected_relevance': ex['expected_relevance'],
            'validation': validation
        }
        # Insert into DB - only store model output if store_in_db is True
        if store_in_db:
            insert_result(
                id=req_id, 
                text=ex['text'], 
                model_output=parsed_output,
                validation=str(validation).lower()
            )
    
    # Calculate and print metrics
    event_accuracy = correct_event / total
    relevance_accuracy = correct_relevance / total
    
    print("\nEvaluation Metrics:")
    print(f"Total examples: {total}")
    print(f"Event accuracy: {event_accuracy:.2%}")
    print(f"Relevance accuracy: {relevance_accuracy:.2%}")
    print("\nConfusion Matrix:")
    for true_event in allowed_events:
        print(f"\nTrue {true_event}:")
        for pred_event in allowed_events:
            count = confusion_matrix[true_event][pred_event]
            if count > 0:
                print(f"  Predicted {pred_event}: {count}")
    
    # Save results to a JSON file
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUTS_DIR, f'evaluation_results_{str(uuid.uuid4())}.json')
    with open(output_file, 'w') as f:
        json.dump({
            'results': results,
            'metrics': {
                'total': total,
                'event_accuracy': event_accuracy,
                'relevance_accuracy': relevance_accuracy,
                'confusion_matrix': confusion_matrix
            }
        }, f, indent=2)
    print(f"\nEvaluation complete! Results saved to '{output_file}'.")

def batch_process_urls(urls, template, model=None, config_path=None, store_in_db=True):
    os.makedirs(DATA_DIR, exist_ok=True)
    config = EventConfig(config_path)
    allowed_events = config.get_event_types()
    results = {}
    for url in urls:
        filename = url.split('/')[-1]
        html_path = os.path.join(DATA_DIR, filename)
        print(f"\nDownloading filing from {url}...")
        download_8k(url, html_path)
        print(f"Extracting text from {html_path}...")
        filing_text = extract_text_from_html(html_path)
        print(f"Classifying event using {template}...")
        result = classify_event(filing_text, allowed_events, template == 'cot.tpl')
        if template == 'zero_shot.tpl':
            validation = validate_zero_shot(result, allowed_events)
        else:
            validation = validate_cot(result, allowed_events)
        # Try to parse model output as JSON
        try:
            parsed_output = json.loads(result)
        except Exception:
            parsed_output = result
        req_id = str(uuid.uuid4())
        results[req_id] = {
            'id': req_id,
            'url': url,
            'model_output': parsed_output,
            'validation': validation
        }
        # Insert into DB
        if store_in_db:
            insert_result(id=req_id, url=url, model_output=parsed_output, validation=str(validation).lower())
        print(f"Model Output: {result}")
        print(f"Validation Result: {validation}")
    output_file = os.path.join(OUTPUTS_DIR, f"batch_results_{str(uuid.uuid4())}.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nBatch results saved to '{output_file}'.")

def main():
    parser = argparse.ArgumentParser(description="SEC 8-K Event Classifier Orchestrator")
    parser.add_argument('--url', type=str, help='URL of the 8-K filing to process')
    parser.add_argument('--url-list', type=str, help='Path to file with one 8-K filing URL per line (batch mode)')
    parser.add_argument('--template', type=str, default='zero_shot.tpl', choices=['zero_shot.tpl', 'cot.tpl'], help='Prompt template to use')
    parser.add_argument('--model', type=str, default=None, help='Ollama model name (default: llama3)')
    parser.add_argument('--ground-truth', action='store_true', help='Run batch evaluation on ground-truth examples')
    parser.add_argument('--config', type=str, help='Path to event configuration file')
    args = parser.parse_args()

    if args.ground_truth:
        # Run batch evaluation on all ground-truth examples
        eval_ground_truth(args.template, args.config, store_in_db=False)
        return

    if args.url_list:
        # Batch process multiple URLs
        with open(args.url_list) as f:
            urls = [line.strip() for line in f if line.strip()]
        batch_process_urls(urls, args.template, model=args.model, config_path=args.config, store_in_db=True)
        return

    if not args.url:
        print("Error: --url or --url-list is required unless --ground-truth is used.")
        sys.exit(1)

    # Step 1: Download the requested SEC filing
    os.makedirs(DATA_DIR, exist_ok=True)
    filename = args.url.split('/')[-1]
    html_path = os.path.join(DATA_DIR, filename)
    print(f"Downloading filing from {args.url}...")
    download_8k(args.url, html_path)

    # Step 2: Extract plain text from the downloaded HTML
    print(f"Extracting text from {html_path}...")
    filing_text = extract_text_from_html(html_path)

    # Step 3: Classify the event(s) in the filing
    config = EventConfig(args.config)
    allowed_events = config.get_event_types()
    print(f"Classifying event using {args.template}...")
    result = classify_event(filing_text, allowed_events, args.template == 'cot.tpl')
    print("\nModel Output:")
    print(result)

    # Step 4: Validate the LLM output
    if args.template == 'zero_shot.tpl':
        validation = validate_zero_shot(result, allowed_events)
    else:
        validation = validate_cot(result, allowed_events)
    print("\nValidation Result:")
    print(validation)

    try:
        parsed_output = json.loads(result)
    except Exception:
        parsed_output = result
    req_id = str(uuid.uuid4())
    single_result = {
        req_id: {
            'id': req_id,
            'url': args.url,
            'model_output': parsed_output,
            'validation': validation
        }
    }
    # Insert into DB
    insert_result(id=req_id, url=args.url, model_output=parsed_output, validation=str(validation).lower())
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUTS_DIR, f"single_result_{str(uuid.uuid4())}.json")
    with open(output_file, 'w') as f:
        json.dump(single_result, f, indent=2)
    print(f"\nSingle result saved to '{output_file}'.")

if __name__ == "__main__":
    main()
