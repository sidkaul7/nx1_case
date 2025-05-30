You are an expert in SEC filings. Please reason step by step:
1. Identify key sentences in the text.
2. For each, map to possible events from {events}. IMPORTANT: You must ONLY use event types from this list. Do not create new event types.
3. For each mapped event, analyze its significance by considering:
   a. Scale/Amount:
      - For acquisitions: Is it a major acquisition or a small one?
      - For transactions: What is the number of shares or dollar amount?
      - For contracts: Is it a major customer or small deal?
   b. Impact:
      - Does it affect company leadership?
      - Does it impact company strategy?
      - Is it a routine administrative event?
   c. Uniqueness:
      - Is this a regular scheduled event?
      - Is it an unexpected or unusual occurrence?
4. Determine relevance based on these criteria:
   - Mark as relevant if:
     * It involves significant amounts (>$1M or >10,000 shares)
     * It affects company leadership (C-suite changes)
     * It's an unusual or unexpected event
     * It impacts company strategy or operations
   - Mark as irrelevant if:
     * It's a routine administrative event
     * It's a small transaction (<$100K or <1,000 shares)
     * It's a regular scheduled event
5. Output a JSON object with 'Reasoning' (list) and 'Events' (array of objects with 'Event Type' and 'Relevant' fields). Example:
{{
  "Reasoning": [
    "The text mentions Apple acquired a major AI startup, which is significant.",
    "The acquisition is of a major AI startup, suggesting it's significant for Apple's future."
  ],
  "Events": [
    {{"Event Type": "Acquisition", "Relevant": true}}
  ]
}}
Do not include any explanation, commentary, or extra text. Output only the JSON object.
If no event is found, return {{"Reasoning": [], "Events": []}}.

IMPORTANT: You must ONLY use event types from the provided list: {events}. Do not create new event types.

Example:
Input: "Apple announced the acquisition of a major AI startup."
Events: ["Acquisition", "Customer Event", "Personnel Change", "Financial Event", "Open Market Purchase", "Open Market Sale", "Option Exercise", "Shares Withheld for Taxes", "Automatic Sale under Rule 10b5-1", "Other"]
Output: {{
  "Reasoning": [
    "Apple acquired a major AI startup, which is an acquisition event.",
    "The acquisition is of a major AI startup, suggesting it's significant for Apple's future."
  ],
  "Events": [
    {{"Event Type": "Acquisition", "Relevant": true}}
  ]
}}

Example:
Input: "Google's CFO will retire at the end of the quarter."
Events: ["Acquisition", "Customer Event", "Personnel Change", "Financial Event", "Open Market Purchase", "Open Market Sale", "Option Exercise", "Shares Withheld for Taxes", "Automatic Sale under Rule 10b5-1", "Other"]
Output: {{
  "Reasoning": [
    "Google's CFO is retiring, which is a personnel change event.",
    "The departure of a CFO is significant as it affects financial leadership."
  ],
  "Events": [
    {{"Event Type": "Personnel Change", "Relevant": true}}
  ]
}}

Example:
Input: "Coca-Cola acquired a minority stake in a beverage startup."
Events: ["Acquisition", "Customer Event", "Personnel Change", "Financial Event", "Open Market Purchase", "Open Market Sale", "Option Exercise", "Shares Withheld for Taxes", "Automatic Sale under Rule 10b5-1", "Other"]
Output: {{
  "Reasoning": [
    "Coca-Cola acquired a minority stake in a beverage startup, which is an acquisition event.",
    "A minority stake in a startup is less significant than a full acquisition."
  ],
  "Events": [
    {{"Event Type": "Acquisition", "Relevant": false}}
  ]
}}

Example:
Input: "Delta Airlines signed a long-term contract with Boeing for new aircraft."
Events: ["Acquisition", "Customer Event", "Personnel Change", "Financial Event", "Open Market Purchase", "Open Market Sale", "Option Exercise", "Shares Withheld for Taxes", "Automatic Sale under Rule 10b5-1", "Other"]
Output: {{
  "Reasoning": [
    "Delta Airlines entered into a significant contract with Boeing, which is a customer event.",
    "A long-term aircraft contract is significant for an airline's operations."
  ],
  "Events": [
    {{"Event Type": "Customer Event", "Relevant": true}}
  ]
}}

Example:
Input: "The CFO of Johnson & Johnson announced her retirement."
Events: ["Acquisition", "Customer Event", "Personnel Change", "Financial Event", "Open Market Purchase", "Open Market Sale", "Option Exercise", "Shares Withheld for Taxes", "Automatic Sale under Rule 10b5-1", "Other"]
Output: {{
  "Reasoning": [
    "The CFO of Johnson & Johnson is retiring, which is a personnel change.",
    "The departure of a CFO is significant as it affects financial leadership."
  ],
  "Events": [
    {{"Event Type": "Personnel Change", "Relevant": true}}
  ]
}}

Example:
Input: "ExxonMobil reported a quarterly loss due to falling oil prices."
Events: ["Acquisition", "Customer Event", "Personnel Change", "Financial Event", "Open Market Purchase", "Open Market Sale", "Option Exercise", "Shares Withheld for Taxes", "Automatic Sale under Rule 10b5-1", "Other"]
Output: {{
  "Reasoning": [
    "ExxonMobil reported a quarterly loss, which is a financial event.",
    "A quarterly loss is significant as it affects the company's financial performance."
  ],
  "Events": [
    {{"Event Type": "Financial Event", "Relevant": true}}
  ]
}}

Example:
Input: "A director at Ford sold 1,500 shares in an open market transaction."
Events: ["Acquisition", "Customer Event", "Personnel Change", "Financial Event", "Open Market Purchase", "Open Market Sale", "Option Exercise", "Shares Withheld for Taxes", "Automatic Sale under Rule 10b5-1", "Other"]
Output: {{
  "Reasoning": [
    "A director at Ford sold shares in an open market transaction, which is an open market sale event.",
    "The sale of 1,500 shares by a director is relatively small and may not be significant."
  ],
  "Events": [
    {{"Event Type": "Open Market Sale", "Relevant": false}}
  ]
}}

Example:
Input: "The company withheld 1,000 shares to cover tax obligations on vested RSUs."
Events: ["Acquisition", "Customer Event", "Personnel Change", "Financial Event", "Open Market Purchase", "Open Market Sale", "Option Exercise", "Shares Withheld for Taxes", "Automatic Sale under Rule 10b5-1", "Other"]
Output: {{
  "Reasoning": [
    "The company withheld shares to cover tax obligations on vested RSUs, which is a shares withheld for taxes event.",
    "This is a routine tax withholding event that occurs with RSU vesting."
  ],
  "Events": [
    {{"Event Type": "Shares Withheld for Taxes", "Relevant": false}}
  ]
}}

Example:
Input: "The CFO sold 5,000 shares pursuant to a pre-established Rule 10b5-1 trading plan."
Events: ["Acquisition", "Customer Event", "Personnel Change", "Financial Event", "Open Market Purchase", "Open Market Sale", "Option Exercise", "Shares Withheld for Taxes", "Automatic Sale under Rule 10b5-1", "Other"]
Output: {{
  "Reasoning": [
    "The CFO sold shares under a Rule 10b5-1 trading plan, which is an automatic sale event.",
    "Rule 10b5-1 plans are pre-established trading plans that are not based on material non-public information."
  ],
  "Events": [
    {{"Event Type": "Automatic Sale under Rule 10b5-1", "Relevant": false}}
  ]
}}

Example:
Input: "A director sold 500 shares to fund a personal expense."
Events: ["Acquisition", "Customer Event", "Personnel Change", "Financial Event", "Open Market Purchase", "Open Market Sale", "Option Exercise", "Shares Withheld for Taxes", "Automatic Sale under Rule 10b5-1", "Other"]
Output: {{
  "Reasoning": [
    "A director sold 500 shares, which is an open market sale event.",
    "The sale of 500 shares is a small transaction (<1,000 shares) and is for personal reasons, making it not significant."
  ],
  "Events": [
    {{"Event Type": "Open Market Sale", "Relevant": false}}
  ]
}}

Example:
Input: "The CEO purchased 15,000 shares in the open market."
Events: ["Acquisition", "Customer Event", "Personnel Change", "Financial Event", "Open Market Purchase", "Open Market Sale", "Option Exercise", "Shares Withheld for Taxes", "Automatic Sale under Rule 10b5-1", "Other"]
Output: {{
  "Reasoning": [
    "The CEO purchased 15,000 shares, which is an open market purchase event.",
    "The purchase of 15,000 shares is a significant amount (>10,000 shares) and involves company leadership, making it relevant."
  ],
  "Events": [
    {{"Event Type": "Open Market Purchase", "Relevant": true}}
  ]
}}

Text:
{text}