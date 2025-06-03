# LLM-Case: SEC Event Classification

## Prompt Optimization & Thought Process

This document outlines the iterative approach taken to develop a robust pipeline for classifying events in SEC Form 8-K filings using a local LLM (Ollama, llama3). The focus throughout was on reliability, extensibility, and practical handling of real-world data.

---

### Objective

- Download and parse 8-K filings (Apple used as a primary example but the system can be pointed at any SEC 8-K URL for event classification)
- Allow user-defined event types and relevance rules (via config)
- Integrate a local LLM for event classification, supporting both zero-shot and chain-of-thought (CoT) prompting
- Validate model output and compare to ground-truth examples
- Ensure modularity for easy adaptation of prompts, models, or event configs
- Extensibility: new event types, prompt templates, or validation logic can be added with minimal changes.

---

### Quick Start

1. **Setup:**
   ```bash
   # Clone the repository
   git clone [repository-url]
   cd llm-case

   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Install Ollama (if not already installed)
   # Follow instructions at https://ollama.ai/download

   # Set environment variables
   export OLLAMA_MODEL=llama3.2:latest  # Specify your preferred model
   ```

2. **Configuration:**
   - Edit `config/events.json` to define your event types and relevance rules
   - Modify `config/ground_truth.json` to add your own test cases
   - Adjust prompt templates in `prompts/` directory if needed

3. **Running the System:**
   ```bash
   # Start the backend server (in one terminal)
   uvicorn api:app --reload --port 8000

   # Start the frontend (in another terminal)
   cd ui
   npm install
   npm start

   # The frontend will be available at http://localhost:3000
   ```

4. **API Endpoints:**
   ```bash
   # Single Filing Classification
   curl -X POST http://localhost:8000/classify/single \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230912.htm"}'

   # Batch Classification
   curl -X POST http://localhost:8000/classify/batch \
     -H "Content-Type: application/json" \
     -d '{"urls": ["url1", "url2"]}'

   # Get All Results
   curl http://localhost:8000/results

   # Get Results by ID
   curl http://localhost:8000/results/{result_id}

   # Get Results by URL
   curl http://localhost:8000/results/url/{url}

   # Delete Single Result
   curl -X DELETE http://localhost:8000/results/{result_id}

   # Delete All Results
   curl -X DELETE http://localhost:8000/results

5. **Frontend Features:**
   - Upload and process single 8-K filings
   - Batch process multiple filings
   - View all classification results in a table
   - Filter and search results by ID or URL
   - Delete individual or all results
   - Toggle columns (ID, prompt type)
   - View model output in a collapsible section

6. **Output:**
   - Results are saved in the `outputs/` directory
   - Each run generates a unique JSON file with classification results
   - Ground truth evaluation includes accuracy metrics and confusion matrix
   - API responses include result IDs for later lookup
   - Frontend provides interactive result viewing and management

7. **Customization:**
   - Add new event types in `config/events.json`
   - Create custom prompt templates in `prompts/`
   - Modify validation rules in `classify/validator.py`
   - Adjust API endpoints in `api.py` for custom functionality
   - Customize frontend components in ui/src/

---

### 1. Initial Prompting and Observations

The initial prompt was direct:
```
You are an expert in SEC filings. Given this text:
{filing_text}
Identify which of these events are described: {events}
Answer with a JSON list of event names.
```
While this approach sometimes produced correct results, the LLM frequently included explanations or non-JSON output, which caused validation failures. There were also cases where the model missed less obvious or ambiguous events.

- ✅ Correct event identification in straightforward cases
- ⚠️ Occasional non-JSON or plain text output
- ⚠️ Missed edge cases or ambiguous phrasing

---

### 2. Improving Output Consistency

To address output variability, I introduced explicit instructions and few-shot examples, instructing the model to output only a valid JSON array. This improved consistency, but the LLM still occasionally included commentary or formatting outside the JSON block.

---

### 3. Incorporating Reasoning and Validation

To enhance interpretability, I implemented a chain-of-thought (CoT) prompt:
```
We want to see your thought process before you answer.
1. Identify key sentences in the filing and quote them
2. Map each sentence to one of these events: {events}
3. Output a JSON object with two fields:
   - "Reasoning": a list of your reasoning steps
   - "Events": a JSON array of objects with 'Event Type' and 'Relevant' fields
```
A Python validator was also developed to ensure the output was valid JSON and only included allowed event types. This step was essential for early detection of output structure issues.

---

### 4. Handling LLM Output Edge Cases

During batch evaluation, I observed that even with specific prompt instructions, the LLM would sometimes prepend or append explanations or formatting to the JSON output. This led to parsing errors such as:
```
Validation error: Expecting value: line 1 column 1 (char 0)
```
This behavior was particularly evident in longer or more complex completions.

---

### 5. Enforcing Strict JSON-Only Output

To mitigate these issues, I refined the prompts further:
- Added explicit instructions: "Do not include any explanation, commentary, or extra text. Output only the JSON array."
- For CoT: "Output only the JSON object."

This significantly reduced formatting errors and improved the reliability of batch validation.

---

### 6. Fallback: Robust JSON Extraction

Recognizing that LLMs may still occasionally produce output outside the strict JSON format, I implemented a fallback in the validator. If direct JSON parsing fails, the validator attempts to extract the first JSON array or object from the output using a regular expression. This approach ensures that even in edge cases, the structured output can be recovered and validated.

```python
import re, json

def extract_json_block(text):
    match = re.search(r'(\[.*?\]|\{.*?\})', text, re.DOTALL)
    if match:
        return match.group(1)
    raise ValueError("No JSON block found in output")
```

---

### 7. Impact of Few-Shot Examples

After observing that the model often failed to identify clear events (such as 'Acquisition') with a strict zero-shot prompt, I added a concrete few-shot example for 'Acquisition' directly to the prompt template. This change led to a significant improvement: the model began to correctly classify acquisition events, outputting the expected JSON structure.

---

#### Further Refinement with Diverse Few-Shot Examples

To further improve the model's generalization and robustness, I added additional few-shot examples to the Chain-of-Thought (CoT) prompt template. These examples use company names and scenarios from a wide range of industries—including technology companies (e.g., Apple, Google, Microsoft), consumer, industrials, healthcare, energy, financials, retail, and transportation (e.g., Coca-Cola, Delta Airlines, Johnson & Johnson, ExxonMobil, Ford, JPMorgan Chase, McDonald's, Merck, FedEx, etc.)—and cover all event types. The ground truth set was also expanded to 100 examples with similar diversity. This refinement led to:

- Improved performance on tech, non-tech, and non-Apple filings
- Better generalization to real-world SEC disclosures across industries
- More reliable event classification across a broader range of companies and situations

---

### 8. Improving Relevance Classification

While the model showed strong performance in event classification, its relevance determination remained inconsistent. Analysis revealed several key issues:

1. Inconsistent Relevance Criteria
   - The model often marked routine events as relevant
   - Significant events were sometimes marked as irrelevant
   - No clear thresholds for determining significance

2. Over-Confidence in Reasoning
   - The model provided reasoning that didn't match its relevance determination
   - Lack of structured analysis for determining significance

To address these issues, the CoT template was enhanced with:

1. Structured Analysis Framework
   - Scale/Amount criteria (e.g., >$1M or >10,000 shares for relevance)
   - Impact assessment (leadership changes, strategy impact)
   - Uniqueness evaluation (routine vs. unusual events)

2. Explicit Relevance Thresholds
   - Clear quantitative thresholds for financial amounts
   - Specific criteria for leadership impact
   - Guidelines for routine vs. significant events

3. Additional Few-Shot Examples
   - Examples demonstrating small vs. large transactions
   - Cases showing clear relevance thresholds
   - Scenarios with mixed significance factors

These improvements led to:
- More consistent relevance determination
- Better alignment between reasoning and relevance decisions
- Clearer quantitative thresholds for significance
- Improved handling of edge cases

---

### 9. Validation and Error Handling

To ensure reliable output, I implemented a robust validation system:

```python
def validate_llm_output(output: str, allowed_events: List[str]) -> Dict:
    """Validates LLM output against expected format and allowed events."""
    try:
        # First attempt: direct JSON parsing
        result = json.loads(output)
    except json.JSONDecodeError:
        # Fallback: extract JSON block using regex
        json_block = extract_json_block(output)
        result = json.loads(json_block)
    
    # Validate structure
    if isinstance(result, list):
        for item in result:
            assert "Event Type" in item, "Missing 'Event Type' field"
            assert "Relevant" in item, "Missing 'Relevant' field"
            assert item["Event Type"] in allowed_events, f"Invalid event: {item['Event Type']}"
    elif isinstance(result, dict):
        assert "Reasoning" in result, "Missing 'Reasoning' field"
        assert "Events" in result, "Missing 'Events' field"
        for event in result["Events"]:
            assert "Event Type" in event, "Missing 'Event Type' field"
            assert "Relevant" in event, "Missing 'Relevant' field"
            assert event["Event Type"] in allowed_events, f"Invalid event: {event['Event Type']}"
    
    return result
```

This validation:
1. Handles both zero-shot (list) and CoT (dict) outputs
2. Provides fallback JSON extraction for malformed responses
3. Validates against allowed event types
4. Returns structured data for further processing

---

### 10. Side-by-Side Comparison: Zero-Shot vs CoT

To demonstrate the difference between approaches, here's the same input processed by both methods:

**Input:**
```
"Apple announced the acquisition of a major AI startup."
```

**Zero-Shot Output:**
```json
[
  {"Event Type": "Acquisition", "Relevant": true}
]
```

**CoT Output:**
```json
{
  "Reasoning": [
    "Apple acquired a major AI startup, which is an acquisition event.",
    "The acquisition is of a major AI startup, suggesting it's significant for Apple's future."
  ],
  "Events": [
    {"Event Type": "Acquisition", "Relevant": true}
  ]
}
```

Key differences:
1. **Reasoning Visibility**: CoT shows the thought process, making it easier to debug and validate
2. **Confidence Level**: CoT provides more context about why the event was classified as significant

### 11. Performance Metrics

Based on evaluation against 100 ground-truth examples, the system demonstrates strong performance:

**Overall Accuracy:**
- Event Type Classification: 92% accuracy
- Relevance Classification: 84% accuracy

**Event Type Classification Performance:**
- Perfect classification (100% accuracy) for:
  - Acquisitions
  - Customer Events
  - Personnel Changes
  - Open Market Purchases
  - Open Market Sales
  - Shares Withheld for Taxes
  - Automatic Sales under Rule 10b5-1
- Strong performance (90% accuracy) for:
  - Option Exercises
- Areas for improvement:
  - Financial Events (70% accuracy, with some confusion between Financial Events and Open Market Purchases/Sales)
  - Other category (70% accuracy, with some confusion with Personnel Changes)

**Relevance Classification:**
- Successfully identifies significant events:
  - Major acquisitions and strategic partnerships
  - C-suite changes and key personnel movements
  - Large transactions (>$1M or >10,000 shares)
  - Unusual or unexpected events
- Correctly flags routine events as not relevant:
  - Scheduled events (earnings calls, regular dividends)
  - Small transactions (<$100K or <1,000 shares)
  - Administrative/boilerplate disclosures
  - Automatic sales under Rule 10b5-1 plans

These results demonstrate the system's effectiveness in accurately classifying both event types and their relevance, with particular strength in identifying material corporate events and filtering out routine disclosures.

---

### 12. Next Steps

To further improve the accuracy and robustness of event type and relevance classification, I would do the following:

- **Support for More LLMs:** Integrate additional or stronger LLMs (e.g., GPT-4, Claude, Gemini) to compare performance, leverage the latest advances in language modeling, and evaluate the impact of using more powerful models than Llama3, especially for complex filings or subtle event/relevance distinctions.
- **Prompt Template Expansion:** Develop and experiment with a wider variety of prompt templates, such as:
  - Adding more diverse few-shot examples covering rare or ambiguous event types
  - Testing alternative reasoning structures (e.g., step-by-step, pros/cons, or tabular reasoning)
  - Comparing the effectiveness of different prompt phrasings and instruction styles to reduce edge-case errors and improve generalization.
- **Advanced Relevance Criteria:** Implement more sophisticated logic for determining event significance, such as:
  - Quantitative thresholds (e.g., "Mark as relevant if acquisition > $10M or > 5% of market cap")
  - Contextual rules (e.g., "Personnel changes are only relevant if C-level or board members are involved")
  - Cross-filing/event aggregation (e.g., "Flag as relevant if similar events occur repeatedly within a quarter")
- **Ongoing Prompt and Validation Refinement:** Continue to iterate on prompt design and output validation as new edge cases and failure modes are discovered in real-world filings.

---

### 13. Example Outputs

**Zero-Shot Example:**
```json
[
  {"Event Type": "Open Market Purchase", "Relevant": true}
]
```

**Chain-of-Thought Example:**
```json
{
  "Reasoning": [
    "A director at Ford sold shares in an open market transaction, which is an open market sale event.",
    "The sale of 1,500 shares by a director is relatively small and may not be significant."
  ],
  "Events": [
    {"Event Type": "Open Market Sale", "Relevant": false}
  ]
}
```

## Running the Application

1. Start the backend API server:
```bash
uvicorn api.main:app --reload
```

2. In a new terminal, start the frontend development server:
```bash
cd frontend
npm install
npm start
```

3. Open your browser and navigate to `http://localhost:5173`

## Command Line Usage

You can also run the classification system directly from the command line. When running Python commands, make sure to use `PYTHONPATH=.` before the command to ensure proper module imports:

```bash
# Ground truth evaluation
PYTHONPATH=. python orchestrator.py --ground-truth --template [zero_shot.tpl or cot.tpl]

# Single filing classification
PYTHONPATH=. python orchestrator.py --url [URL] --template [zero_shot.tpl or cot.tpl]

# Batch processing
PYTHONPATH=. python orchestrator.py --batch [FILE] --template [zero_shot.tpl or cot.tpl]
```

Note: The `--template` argument is optional and defaults to 'zero_shot.tpl'. Available templates are:
- `zero_shot.tpl`: Direct classification without reasoning
- `cot.tpl`: Chain-of-thought classification with detailed reasoning