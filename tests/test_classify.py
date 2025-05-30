from classify.classify import classify_event, load_event_types

def test_classify_event_real_llm():
    # Test classify_event with the real LLM and a known acquisition event
    events = load_event_types()
    result = classify_event("Apple acquired a company.", events, use_cot=False)
    assert isinstance(result, list)
    assert any(event["Event Type"] == "Acquisition" for event in result)

def test_classify_event_different_event(monkeypatch):
    # Test classify_event with a mocked LLM for a personnel change event
    from classify import classify
    events = load_event_types()
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '[{"Event Type": "Personnel Change", "Relevant": false}]')
    result = classify_event("The CFO resigned.", events, use_cot=False)
    assert any(event["Event Type"] == "Personnel Change" for event in result)

def test_classify_event_empty_input(monkeypatch):
    # Test classify_event with a mocked LLM and empty input
    from classify import classify
    events = load_event_types()
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '[]')
    result = classify_event("", events, use_cot=False)
    assert result == []

def test_classify_event_zero_shot_diverse_companies(monkeypatch):
    from classify import classify
    events = load_event_types()
    
    # Apple Acquisition
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '[{"Event Type": "Acquisition", "Relevant": true}]')
    result = classify_event("Apple announced the acquisition of a major AI startup.", events, use_cot=False)
    assert any(event["Event Type"] == "Acquisition" and event["Relevant"] for event in result)
    
    # Google Personnel Change
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '[{"Event Type": "Personnel Change", "Relevant": true}]')
    result = classify_event("Google's CFO will retire at the end of the quarter.", events, use_cot=False)
    assert any(event["Event Type"] == "Personnel Change" and event["Relevant"] for event in result)
    
    # Coca-Cola Acquisition
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '[{"Event Type": "Acquisition", "Relevant": false}]')
    result = classify_event("Coca-Cola acquired a minority stake in a beverage startup.", events, use_cot=False)
    assert any(event["Event Type"] == "Acquisition" and not event["Relevant"] for event in result)
    
    # Delta Airlines Customer Event
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '[{"Event Type": "Customer Event", "Relevant": true}]')
    result = classify_event("Delta Airlines signed a long-term contract with Boeing for new aircraft.", events, use_cot=False)
    assert any(event["Event Type"] == "Customer Event" and event["Relevant"] for event in result)
    
    # ExxonMobil Financial Event
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '[{"Event Type": "Financial Event", "Relevant": true}]')
    result = classify_event("ExxonMobil reported a quarterly loss due to falling oil prices.", events, use_cot=False)
    assert any(event["Event Type"] == "Financial Event" and event["Relevant"] for event in result)
    
    # Ford Open Market Sale
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '[{"Event Type": "Open Market Sale", "Relevant": false}]')
    result = classify_event("A director at Ford sold 1,500 shares in an open market transaction.", events, use_cot=False)
    assert any(event["Event Type"] == "Open Market Sale" and not event["Relevant"] for event in result)

def test_classify_event_cot_diverse_companies(monkeypatch):
    from classify import classify
    events = load_event_types()
    
    # Apple Acquisition (CoT)
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '{"Reasoning": ["Apple acquired a major AI startup, which is an acquisition event.", "The acquisition is of a major AI startup, suggesting it\'s significant for Apple\'s future."], "Events": [{"Event Type": "Acquisition", "Relevant": true}]}')
    result = classify_event("Apple announced the acquisition of a major AI startup.", events, use_cot=True)
    assert result["Events"][0]["Event Type"] == "Acquisition" and result["Events"][0]["Relevant"]
    
    # Google Personnel Change (CoT)
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '{"Reasoning": ["Google\'s CFO is retiring, which is a personnel change event.", "The departure of a CFO is significant as it affects financial leadership."], "Events": [{"Event Type": "Personnel Change", "Relevant": true}]}')
    result = classify_event("Google's CFO will retire at the end of the quarter.", events, use_cot=True)
    assert result["Events"][0]["Event Type"] == "Personnel Change" and result["Events"][0]["Relevant"]
    
    # Coca-Cola Acquisition (CoT)
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '{"Reasoning": ["Coca-Cola acquired a minority stake in a beverage startup, which is an acquisition event.", "A minority stake in a startup is less significant than a full acquisition."], "Events": [{"Event Type": "Acquisition", "Relevant": false}]}')
    result = classify_event("Coca-Cola acquired a minority stake in a beverage startup.", events, use_cot=True)
    assert result["Events"][0]["Event Type"] == "Acquisition" and not result["Events"][0]["Relevant"]
    
    # Delta Airlines Customer Event (CoT)
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '{"Reasoning": ["Delta Airlines entered into a significant contract with Boeing, which is a customer event.", "A long-term aircraft contract is significant for an airline\'s operations."], "Events": [{"Event Type": "Customer Event", "Relevant": true}]}')
    result = classify_event("Delta Airlines signed a long-term contract with Boeing for new aircraft.", events, use_cot=True)
    assert result["Events"][0]["Event Type"] == "Customer Event" and result["Events"][0]["Relevant"]
    
    # ExxonMobil Financial Event (CoT)
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '{"Reasoning": ["ExxonMobil reported a quarterly loss, which is a financial event.", "A quarterly loss is significant as it affects the company\'s financial performance."], "Events": [{"Event Type": "Financial Event", "Relevant": true}]}')
    result = classify_event("ExxonMobil reported a quarterly loss due to falling oil prices.", events, use_cot=True)
    assert result["Events"][0]["Event Type"] == "Financial Event" and result["Events"][0]["Relevant"]
    
    # Ford Open Market Sale (CoT)
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '{"Reasoning": ["A director at Ford sold shares in an open market transaction, which is an open market sale event.", "The sale of 1,500 shares by a director is relatively small and may not be significant."], "Events": [{"Event Type": "Open Market Sale", "Relevant": false}]}')
    result = classify_event("A director at Ford sold 1,500 shares in an open market transaction.", events, use_cot=True)
    assert result["Events"][0]["Event Type"] == "Open Market Sale" and not result["Events"][0]["Relevant"]

# --- REAL LLM TESTS (integration) ---
def test_real_llm_zero_shot_apple():
    events = load_event_types()
    result = classify_event("Apple announced the acquisition of a major AI startup.", events, use_cot=False)
    assert isinstance(result, list)
    assert any(event["Event Type"] == "Acquisition" for event in result)

def test_real_llm_zero_shot_google():
    events = load_event_types()
    result = classify_event("Google's CFO will retire at the end of the quarter.", events, use_cot=False)
    assert isinstance(result, list)
    assert any(event["Event Type"] == "Personnel Change" for event in result)

def test_real_llm_zero_shot_cocacola():
    events = load_event_types()
    result = classify_event("Coca-Cola acquired a minority stake in a beverage startup.", events, use_cot=False)
    assert isinstance(result, list)
    assert any(event["Event Type"] == "Acquisition" for event in result)

def test_real_llm_zero_shot_delta():
    events = load_event_types()
    result = classify_event("Delta Airlines signed a long-term contract with Boeing for new aircraft.", events, use_cot=False)
    assert isinstance(result, list)
    assert any(event["Event Type"] == "Customer Event" for event in result)

def test_real_llm_zero_shot_option_exercise():
    events = load_event_types()
    result = classify_event("The CEO exercised options to purchase 10,000 shares at $150 per share.", events, use_cot=False)
    assert isinstance(result, list)
    assert any(event["Event Type"] == "Option Exercise" for event in result)

def test_real_llm_zero_shot_shares_withheld():
    events = load_event_types()
    result = classify_event("The company withheld 1,000 shares to cover tax obligations on vested RSUs.", events, use_cot=False)
    assert isinstance(result, list)
    assert any(event["Event Type"] == "Shares Withheld for Taxes" for event in result)

def test_real_llm_zero_shot_automatic_sale():
    events = load_event_types()
    result = classify_event("The CFO sold 5,000 shares pursuant to a pre-established Rule 10b5-1 trading plan.", events, use_cot=False)
    assert isinstance(result, list)
    assert any(event["Event Type"] == "Automatic Sale under Rule 10b5-1" for event in result)

# --- MOCKED LLM TESTS (unit, fast) ---
def test_mocked_llm_zero_shot_exxon(monkeypatch):
    from classify import classify
    events = load_event_types()
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '[{"Event Type": "Financial Event", "Relevant": true}]')
    result = classify_event("ExxonMobil reported a quarterly loss due to falling oil prices.", events, use_cot=False)
    assert any(event["Event Type"] == "Financial Event" for event in result)

def test_mocked_llm_zero_shot_ford(monkeypatch):
    from classify import classify
    events = load_event_types()
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '[{"Event Type": "Open Market Sale", "Relevant": false}]')
    result = classify_event("A director at Ford sold 1,500 shares in an open market transaction.", events, use_cot=False)
    assert any(event["Event Type"] == "Open Market Sale" for event in result)

# --- REAL LLM TESTS (integration, CoT) ---
def test_real_llm_cot_apple():
    events = load_event_types()
    result = classify_event("Apple announced the acquisition of a major AI startup.", events, use_cot=True)
    assert isinstance(result, dict)
    assert result["Events"][0]["Event Type"] == "Acquisition"

def test_real_llm_cot_google():
    events = load_event_types()
    result = classify_event("Google's CFO will retire at the end of the quarter.", events, use_cot=True)
    assert isinstance(result, dict)
    assert result["Events"][0]["Event Type"] == "Personnel Change"

def test_real_llm_cot_cocacola():
    events = load_event_types()
    result = classify_event("Coca-Cola acquired a minority stake in a beverage startup.", events, use_cot=True)
    assert isinstance(result, dict)
    assert result["Events"][0]["Event Type"] == "Acquisition"

def test_real_llm_cot_delta():
    events = load_event_types()
    result = classify_event("Delta Airlines signed a long-term contract with Boeing for new aircraft.", events, use_cot=True)
    assert isinstance(result, dict)
    assert result["Events"][0]["Event Type"] == "Customer Event"

def test_real_llm_cot_option_exercise():
    events = load_event_types()
    result = classify_event("The CEO exercised options to purchase 10,000 shares at $150 per share.", events, use_cot=True)
    assert isinstance(result, dict)
    assert result["Events"][0]["Event Type"] == "Option Exercise"

def test_real_llm_cot_shares_withheld():
    events = load_event_types()
    result = classify_event("The company withheld 1,000 shares to cover tax obligations on vested RSUs.", events, use_cot=True)
    assert isinstance(result, dict)
    assert result["Events"][0]["Event Type"] == "Shares Withheld for Taxes"

def test_real_llm_cot_automatic_sale():
    events = load_event_types()
    result = classify_event("The CFO sold 5,000 shares pursuant to a pre-established Rule 10b5-1 trading plan.", events, use_cot=True)
    assert isinstance(result, dict)
    assert result["Events"][0]["Event Type"] == "Automatic Sale under Rule 10b5-1"

# --- MOCKED LLM TESTS (unit, fast, CoT) ---
def test_mocked_llm_cot_exxon(monkeypatch):
    from classify import classify
    events = load_event_types()
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '{"Reasoning": ["ExxonMobil reported a quarterly loss, which is a financial event.", "A quarterly loss is significant as it affects the company\'s financial performance."], "Events": [{"Event Type": "Financial Event", "Relevant": true}]}')
    result = classify_event("ExxonMobil reported a quarterly loss due to falling oil prices.", events, use_cot=True)
    assert result["Events"][0]["Event Type"] == "Financial Event" and result["Events"][0]["Relevant"]

def test_mocked_llm_cot_ford(monkeypatch):
    from classify import classify
    events = load_event_types()
    monkeypatch.setattr(classify, "run_llama3", lambda prompt: '{"Reasoning": ["A director at Ford sold shares in an open market transaction, which is an open market sale event.", "The sale of 1,500 shares by a director is relatively small and may not be significant."], "Events": [{"Event Type": "Open Market Sale", "Relevant": false}]}')
    result = classify_event("A director at Ford sold 1,500 shares in an open market transaction.", events, use_cot=True)
    assert result["Events"][0]["Event Type"] == "Open Market Sale" and not result["Events"][0]["Relevant"] 