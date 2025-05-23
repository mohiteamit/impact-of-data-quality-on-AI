import os
import random
import uuid
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("DEEPSEEK_API_KEY")
api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")

# Initialize OpenAI client with DeepSeek configuration
client = OpenAI(
    api_key=api_key,
    base_url=api_base
)

def generate_bad_data(json_str):
    data = json.loads(json_str)
    bad_data = {
        "survey_id": str(uuid.uuid4()),
        "survey_blob": ""
    }
    
    blobs = []
    for q in data['questions']:
        blob_parts = [
            q.get('question_text', ''),
            "Options: " + "; ".join(q.get('answer_options', [])),
            "Routing: " + q.get('routing_logic', ''),
            "Client Note: " + q.get('client_notes', ''),
            "Scripter Note: " + q.get('scripter_notes', ''),
            "Script: " + json.dumps(q.get('script', {}), ensure_ascii=False)
        ]
        
        # Randomly drop some blob parts (simulate missing info)
        blob_parts = [part for part in blob_parts if random.random() > 0.2]

        # Randomly shuffle blob parts
        random.shuffle(blob_parts)

        # Combine parts into a question blob
        question_blob = " | ".join(blob_parts)
        blobs.append(question_blob)

    # Randomly shuffle questions to remove ordered context
    random.shuffle(blobs)

    # Combine question blobs into single survey blob
    bad_data["survey_blob"] = blobs

    return bad_data["survey_blob"]


from rich.progress import Progress, TimeElapsedColumn, BarColumn, TextColumn, SpinnerColumn
from pathlib import Path
import json
import uuid
import logging
import time

# Configure logging
log_path = Path("logs")
log_path.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=log_path / "generate_examples.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def generate_examples(prompt_file_path, n_examples=1, model="deepseek-reasoner", temperature=0.7,  
                      success_dir="data/good", failed_dir="data/good/failed"):
    prompt_path = Path(prompt_file_path)
    success_path = Path(success_dir)
    failed_path = Path(failed_dir)
    success_path.mkdir(parents=True, exist_ok=True)
    failed_path.mkdir(parents=True, exist_ok=True)

    previous_topics = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:

        overall_task = progress.add_task("[green]Generating examples", total=n_examples)

        for i in range(n_examples):
            start_time = time.time()

            try:
                # -----------------------------
                # Step 1: Prepare Prompt
                # -----------------------------
                with open(prompt_path, "r", encoding="utf-8") as f:
                    prompt_template = f.read().strip()

                exclusion_text = (
                    '\n'.join(f'- "{topic}"' for topic in previous_topics)
                    if previous_topics else ""
                )

                updated_prompt_content = prompt_template.replace(
                    "<PREVIOUSLY_GENERATED_SURVEY_NAME>", exclusion_text
                ) if previous_topics else prompt_template.replace(
                    "especially the following:\n- <PREVIOUSLY_GENERATED_SURVEY_NAME>\n", ""
                )

                # -----------------------------
                # Step 2: API Call
                # -----------------------------
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": updated_prompt_content}],
                    temperature=temperature,
                )

                # -----------------------------
                # Step 3: Clean & Validate JSON
                # -----------------------------
                response_text = response.choices[0].message.content
                cleaned_text = response_text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()

                try:
                    parsed_data = json.loads(cleaned_text)
                    parsed_data['survey_id'] = str(uuid.uuid4())
                    cleaned_text = json.dumps(parsed_data, ensure_ascii=False, indent=4)

                    new_topic = parsed_data.get('survey_name')
                    if new_topic:
                        previous_topics.append(new_topic)
                        previous_topics = previous_topics[-500:]

                    is_valid_json = True

                    # Log generated survey topic
                    logging.info(f"Generated Topic #{i+1}: {new_topic}")

                except json.JSONDecodeError as json_err:
                    logging.error(f"[Example #{i+1}] JSON Decode Error: {json_err}")
                    is_valid_json = False

                # -----------------------------
                # Step 4: Save Survey JSON
                # -----------------------------
                output_dir = success_path if is_valid_json else failed_path
                output_file = output_dir / f"{parsed_data['survey_id'] if is_valid_json else uuid.uuid4()}.json"

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(cleaned_text)

                elapsed_time = time.time() - start_time
                logging.info(
                    f"[Example #{i+1}] Status: {'valid' if is_valid_json else 'invalid'} - Elapsed: {elapsed_time:.2f}s"
                )

                progress.update(
                    overall_task, 
                    advance=1, 
                    description=f"[green]Example {i+1}/{n_examples} - Last: {'valid' if is_valid_json else 'invalid'}"
                )

            except Exception as e:
                elapsed_time = time.time() - start_time
                logging.exception(f"[Example #{i+1}] Unhandled Exception: {e}")

                progress.update(
                    overall_task, 
                    advance=1, 
                    description=f"[red]Example {i+1}/{n_examples} - Last: error"
                )

    print("Generation completed! Logs available at logs/generate_examples.log")

generate_examples(
    prompt_file_path='prompts/deepseek-good-data.md',
    model="deepseek-chat",
    n_examples=2000, 
    temperature=1.5
)
