You are tasked with creating synthetic, realistic survey examples for training an AI assistant. Follow these steps carefully:

### Step 1: Use Provided Survey Topic

A specific survey topic is provided below:

Topic: "<INSERT_TOPIC_HERE>"

Proceed to create the survey based exclusively on this provided topic. Ensure the survey is clearly relevant and directly aligned with the provided topic.

### Step 2: Create a Survey

* Build one complete survey on the selected topic.
* Include **between 10 and 20 realistic survey questions**.

### Step 3: Structure the Survey Data

Structure the survey clearly and strictly following this JSON schema:

```json
{
  "survey_id": "<Unique alphanumeric ID, e.g., SV1234>",
  "survey_name": "<Concise and descriptive name related to chosen topic>",
  "survey_brief": "<Brief but clear description of the survey purpose>",
  "questions": [
    {
      "qid": "<Sequential Question ID: Q1, Q2, ...>",
      "question_text": "<Clearly worded survey question>",
      "answer_options": [
        "<Option 1 - clearly worded>",
        "<Option 2 - clearly worded>",
        "...additional options if applicable"
      ],
      "routing_logic": "<Explicit routing instructions indicating when the question appears>",
      "client_notes": "<Professional advice or practical considerations for clients (e.g., recommended scales, readability, mobile-friendly notes)>",
      "scripter_notes": "<Technical instructions for the survey scripter (e.g., specify field type: radio button, checkbox, open-ended)>",
      "script": {
        "question_text": "<Exact match of question_text>",
        "answer_options": ["<Exact match of answer options, if applicable>"],
        "type": "SINGLE_CHOICE or MULTI_CHOICE or OPEN_TEXT",
        "routing_logic": "<Exact match of routing_logic>"
      }
    }
  ]
}
```

### Important Details for Each Survey:

* Include varied question types (single-choice, multi-choice, open-ended).
* Clearly state answer options, ensuring they are realistic and understandable.
* Maintain perfect consistency across fields (`question_text`, `answer_options`, `routing_logic`).

### Important Instructions for the `"script"` field:

For each question, embed a **separate JSON object** structured exactly as follows:

* **Single-choice or Multi-choice Questions:**

```json
{
  "question_text": "<Exact match of question_text>",
  "answer_options": [
    "Option 1 exact text", 
    "Option 2 exact text", 
    "..."
  ],
  "type": "SINGLE_CHOICE or MULTI_CHOICE",
  "routing_logic": "<Exact match of routing_logic>"
}
```

* **Open-ended Questions (no options):**

```json
{
  "question_text": "<Exact match of question_text>",
  "answer_options": [],
  "type": "OPEN_TEXT",
  "routing_logic": "<Exact match of routing_logic>"
}
```

**Important:**

* Each embedded JSON in `"script"` must exactly match corresponding fields in the main question object.
* Maintain strict JSON correctness.

Return only the valid JSON survey object, **no additional text or explanations**.
