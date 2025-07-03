'''Helper functions for the agent(s) in the GAIA question answering system.'''

import os
import time
import json
import logging
from openai import OpenAI
from smolagents import CodeAgent, ActionStep, MessageRole
from configuration import CHECK_MODEL, TOKEN_LIMITER, STEP_WAIT

# Get logger for this module
logger = logging.getLogger(__name__)


def check_reasoning(final_answer:str, agent_memory):
    """Checks the reasoning and plot of the agent's final answer."""

    prompt = (
        f"Here is a user-given task and the agent steps: {agent_memory.get_succinct_steps()}. " +
        "Please check that the reasoning process and answer are correct. " +
        "Do they correctly answer the given task? " +
        "First list reasons why yes/no, then write your final decision: " +
        "PASS in caps lock if it is satisfactory, FAIL if it is not. " +
        f"Final answer: {str(final_answer)}"
    )

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                }
            ],
        }
    ]

    output = CHECK_MODEL(messages).content
    print("Feedback: ", output)

    if "FAIL" in output:
        raise Exception(output) # pylint:disable=broad-exception-raised

    return True


def step_memory_cap(memory_step: ActionStep, agent: CodeAgent) -> None:
    '''Removes old steps from agent memory to keep context length under control.'''

    task_step = agent.memory.steps[0]
    planning_step = agent.memory.steps[1]
    latest_step = agent.memory.steps[-1]

    if len(agent.memory.steps) > 2:
        agent.memory.steps = [task_step, planning_step, latest_step]

    logger.info('Agent memory has %d steps', len(agent.memory.steps))
    logger.info('Latest step is step %d', memory_step.step_number)
    logger.info('Contains: %s messages', len(agent.memory.steps[-1].model_input_messages))
    logger.info('Token usage: %s', agent.memory.steps[-1].token_usage.total_tokens)

    for message in agent.memory.steps[-1].model_input_messages:
        logger.debug(' Role: %s: %s', message['role'], message['content'][:100])

    token_usage = agent.memory.steps[-1].token_usage.total_tokens

    if token_usage > TOKEN_LIMITER:
        logger.info('Token usage is %d, summarizing old messages', token_usage)

        summary = summarize_old_messages(
            agent.memory.steps[-1].model_input_messages[1:]
        )

        if summary is not None:

            new_messages = [agent.memory.steps[-1].model_input_messages[0]]
            new_messages.append({
                'role': MessageRole.USER,
                'content': [{
                    'type': 'text',
                    'text': f'Here is a summary of your investigation so far: {summary}'
                }]
            })
            agent.memory.steps = [agent.memory.steps[0]]
            agent.memory.steps[0].model_input_messages = new_messages

        for message in agent.memory.steps[0].model_input_messages:
            logger.debug(' Role: %s: %s', message['role'], message['content'][:100])


def summarize_old_messages(messages: dict) -> dict:
    '''Summarizes old messages to keep context length under control.'''

    client = OpenAI(api_key=os.environ['MODAL_API_KEY'])

    client.base_url = (
        'https://gperdrizet--vllm-openai-compatible-summarization-serve.modal.run/v1'
    )

    # Default to first avalible model
    model = client.models.list().data[0]
    model_id = model.id

    messages = [
        {
            'role': 'system',
            'content': ('Summarize the following interaction between an AI agent and a user.' +
                f'Return the summary formatted as text, not as JSON: {json.dumps(messages)}')
        }
    ]

    completion_args = {
        'model': model_id,
        'messages': messages,
    }

    try:
        response = client.chat.completions.create(**completion_args)

    except Exception as e: # pylint: disable=broad-exception-caught
        response = None
        logger.error('Error during Modal API call: %s', e)

    if response is not None:
        summary = response.choices[0].message.content

    else:
        summary = None

    return summary

def step_wait(memory_step: ActionStep, agent: CodeAgent) -> None:
    '''Waits for a while to prevent hitting API rate limits.'''

    logger.info('Waiting for %d seconds to prevent hitting API rate limits', STEP_WAIT)
    logger.info('Current step is %d', memory_step.step_number)
    logger.info('Current agent has %d steps', len(agent.memory.steps))

    time.sleep(STEP_WAIT)

    return True
