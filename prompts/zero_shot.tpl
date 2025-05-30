You are an expert in SEC filings. Given the following disclosure text:
{text}

Identify which of these event types are described in the text: {events}

Return your answer as a JSON array of objects with 'Event Type' and 'Relevant' fields. Example:
[
  {{"Event Type": "Acquisition", "Relevant": true}},
  {{"Event Type": "Other", "Relevant": false}}
]
Do not include any explanation, commentary, or extra text. Output only the JSON array.
If no event is found, return an empty array.
