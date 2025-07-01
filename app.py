'''HuggingFace Agents course final project GAIA agent benchmark.'''

# Standard library
import glob
import logging
import os
import requests

# Third-party
import gradio as gr
import pandas as pd

# Local/Project
from functions.agent import create_agent

# --- Constants ---
from configuration import QUESTIONS, DEFAULT_API_URL, INSTRUCTIONS

# --- Logging Configuration ---
# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Clean up old log files
def cleanup_old_logs():
    """Remove old log files from the logs directory."""
    log_files = glob.glob('logs/*.log')
    for log_file in log_files:
        try:
            os.remove(log_file)
            print(f"Removed old log file: {log_file}")
        except OSError as e:
            print(f"Error removing log file {log_file}: {e}")

# Clean up old logs before starting
cleanup_old_logs()

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent.log', encoding='utf-8'),
        logging.StreamHandler()  # Also log to console
    ]
)

# Get logger for this module
logger = logging.getLogger(__name__)


def run_and_submit_all(profile: gr.OAuthProfile | None):
    """
    Fetches all questions, runs the BasicAgent on them, submits all answers,
    and displays the results.
    """
    # --- Determine HF Space Runtime URL and Repo URL ---
    space_id = os.getenv('SPACE_ID')

    if profile:
        username = f'{profile.username}'
        logger.info('User logged in: %s', username)
    else:
        logger.warning('User not logged in.')
        return 'Please Login to Hugging Face with the button.', None

    api_url = DEFAULT_API_URL
    questions_url = f'{api_url}/questions'
    submit_url = f'{api_url}/submit'

    # 1. Instantiate Agent (imported from agent.py)
    try:
        agent = create_agent()
    except Exception as e: # pylint: disable=W0703
        logger.error("Error instantiating agent: %s", e)
        return f"Error initializing agent: {e}", None

    # In the case of an app running as a hugging Face space, this link points toward your
    # codebase (useful for others so please keep it public)
    agent_code = f'https://huggingface.co/spaces/{space_id}/tree/main'
    logger.info('Agent code URL: %s', agent_code)

    # 2. Fetch Questions
    logger.info('Fetching questions from: %s', questions_url)

    try:
        response = requests.get(questions_url, timeout=15)
        response.raise_for_status()
        questions_data = response.json()

        if not questions_data:
            logger.warning('Fetched questions list is empty.')
            return 'Fetched questions list is empty or invalid format.', None

        logger.info('Fetched %d questions.', len(questions_data))

    except requests.exceptions.JSONDecodeError as e:
        logger.error('Error decoding JSON response from questions endpoint: %s', e)
        logger.debug('Response text: %s', response.text[:500])
        return f'Error decoding server response for questions: {e}', None

    except requests.exceptions.RequestException as e:
        logger.error('Error fetching questions: %s', e)
        return f'Error fetching questions: {e}', None

    except Exception as e: # pylint: disable=W0703
        logger.error('An unexpected error occurred fetching questions: %s', e)
        return f'An unexpected error occurred fetching questions: {e}', None

    with open('questions.json', 'w', encoding='utf-8') as f:
        # Save the fetched questions to a file for debugging purposes
        pd.DataFrame(questions_data).to_json(f, orient='records', lines=True, force_ascii=False)

    # 3. Run your Agent
    results_log = []
    answers_payload = []

    logger.info('Running agent on %d questions...', len(questions_data))

    for question_number in QUESTIONS:
        item = questions_data[question_number - 1]  # Adjust for zero-based index
        task_id = item.get("task_id")
        question_text = item.get("question")

        if not task_id or question_text is None:
            logger.warning('Skipping item with missing task_id or question: %s', item)
            continue

        try:
            submitted_answer = agent.run(
                INSTRUCTIONS + '\n' + question_text
            )

            answers_payload.append({"task_id": task_id, "submitted_answer": submitted_answer})
            results_log.append({
                "Task ID": task_id,
                "Question": question_text,
                "Submitted Answer": submitted_answer
            })

        except Exception as e: # pylint: disable=W0703
            logger.error('Error running agent on task %s: %s', task_id, e)
            results_log.append({
                 "Task ID": task_id,
                 "Question": question_text,
                 "Submitted Answer": f"AGENT ERROR: {e}"
             })

    if not answers_payload:
        logger.warning('Agent did not produce any answers to submit.')
        return 'Agent did not produce any answers to submit.', pd.DataFrame(results_log)

    # 4. Prepare Submission
    submission_data = {
        "username": username.strip(),
        "agent_code": agent_code,
        "answers": answers_payload
    }
    status_update = (
        f'Agent finished. Submitting {len(answers_payload)} answers for user "{username}"...'
    )
    logger.info(status_update)

    # 5. Submit
    logger.info('Submitting %d answers to: %s', len(answers_payload), submit_url)
    try:
        response = requests.post(submit_url, json=submission_data, timeout=60)
        response.raise_for_status()
        result_data = response.json()
        final_status = (
            f"Submission Successful!\n"
            f"User: {result_data.get('username')}\n"
            f"Overall Score: {result_data.get('score', 'N/A')}% "
            f"({result_data.get('correct_count', '?')}/"
            f"{result_data.get('total_attempted', '?')} correct)\n"
            f"Message: {result_data.get('message', 'No message received.')}"
        )
        logger.info('Submission successful.')
        results_df = pd.DataFrame(results_log)
        results_df.to_csv('results.csv', index=False)
        return final_status, results_df

    except requests.exceptions.HTTPError as e:
        error_detail = f"Server responded with status {e.response.status_code}."

        try:
            error_json = e.response.json()
            error_detail += f" Detail: {error_json.get('detail', e.response.text)}"

        except requests.exceptions.JSONDecodeError:
            error_detail += f" Response: {e.response.text[:500]}"

        status_message = f"Submission Failed: {error_detail}"
        logger.error(status_message)
        results_df = pd.DataFrame(results_log)
        results_df.to_csv('results.csv', index=False)
        return status_message, results_df

    except requests.exceptions.Timeout:
        status_message = "Submission Failed: The request timed out."
        logger.error(status_message)
        results_df = pd.DataFrame(results_log)
        results_df.to_csv('results.csv', index=False)
        return status_message, results_df

    except requests.exceptions.RequestException as e:
        status_message = f"Submission Failed: Network error - {e}"
        logger.error(status_message)
        results_df = pd.DataFrame(results_log)
        results_df.to_csv('results.csv', index=False)
        return status_message, results_df

    except Exception as e: # pylint: disable=W0703
        status_message = f"An unexpected error occurred during submission: {e}"
        logger.error(status_message)
        results_df = pd.DataFrame(results_log)
        results_df.to_csv('results.csv', index=False)
        return status_message, results_df


# --- Build Gradio Interface using Blocks ---
with gr.Blocks() as demo:
    gr.Markdown("# Basic Agent Evaluation Runner")
    gr.Markdown(
        """
        **Instructions:**

        1.  Please clone this space, then modify the code to define your agent's logic, 
            the tools, the necessary packages, etc ...
        2.  Log in to your Hugging Face account using the button below. This uses your 
            HF username for submission.
        3.  Click 'Run Evaluation & Submit All Answers' to fetch questions, run your 
            agent, submit answers, and see the score.

        ---
        **Disclaimers:**
        Once clicking on the "submit" button, it can take quite some time (this is the 
        time for the agent to go through all the questions).
        This space provides a basic setup and is intentionally sub-optimal to encourage
        you to develop your own, more robust solution. For instance, for the delay process
        of the submit button, a solution could be to cache the answers and submit in a 
        separate action or even to answer the questions in async.
        """
    )

    gr.LoginButton()

    run_button = gr.Button("Run Evaluation & Submit All Answers")

    status_output = gr.Textbox(label="Run Status / Submission Result", lines=5, interactive=False)
    results_table = gr.DataFrame(label="Questions and Agent Answers", wrap=True)

    run_button.click( # pylint: disable=E1101
        fn=run_and_submit_all,
        outputs=[status_output, results_table]
    )

if __name__ == "__main__":

    # Check for SPACE_HOST and SPACE_ID at startup for information
    space_host_startup = os.getenv("SPACE_HOST")
    space_id_startup = os.getenv("SPACE_ID") # Get SPACE_ID at startup

    if space_host_startup:
        logger.info("✅ SPACE_HOST found: %s", space_host_startup)
        logger.info("   Runtime URL should be: https://%s.hf.space", space_host_startup)
    else:
        logger.info("ℹ️  SPACE_HOST environment variable not found (running locally?).")

    if space_id_startup: # Print repo URLs if SPACE_ID is found
        logger.info("✅ SPACE_ID found: %s", space_id_startup)
        logger.info("   Repo URL: https://huggingface.co/spaces/%s", space_id_startup)
        logger.info(
            "   Repo Tree URL: https://huggingface.co/spaces/%s/tree/main",
              space_id_startup
        )

    else:
        logger.info(
            "ℹ️  SPACE_ID environment variable not found (running locally?). " \
            "Repo URL cannot be determined."
        )

    logger.info("Launching Gradio Interface for Basic Agent Evaluation...")
    demo.launch(debug=True, share=False)
