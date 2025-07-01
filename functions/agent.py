'''Agent definition for GAIA question answering system.'''

# Standard library
import os
import json
import logging

from openai import OpenAI

# Imports for agent creation
from smolagents import CodeAgent, InferenceClientModel, VisitWebpageTool, ActionStep, MessageRole
from functions.tools import (
    google_search,
    wikipedia_search,
    get_wikipedia_page
)

# Get logger for this module
logger = logging.getLogger(__name__)

def create_agent():
    '''Creates agent for GAIA question answering system.'''

    model = InferenceClientModel(
        "deepseek-ai/DeepSeek-V3",
        provider="together",
        max_tokens=64000
    )

    tools = [
        wikipedia_search,
        get_wikipedia_page,
        google_search,
        VisitWebpageTool(),
    ]

    agent = CodeAgent(
        model=model,
        tools=tools,
        additional_authorized_imports=['bs4.*', 'json'],
        step_callbacks=[step_memory_cap],
        name="GAIA_agent",
        verbosity_level=5,
        max_steps=30,
        planning_interval=2,
        description="GAIA agent for question answering"
    )


    return agent


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

    if token_usage > 50000:
        logger.info('Token usage is %d, summarizing old messages', token_usage)

        summary = summarize_old_messages(
            agent.memory.steps[-1].model_input_messages[1:]
        )

        if summary is not None:

            new_messages = [agent.memory.steps[-1].model_input_messages[0]]
            new_messages.append({
                'role': MessageRole.USER,
                'content': [{'type': 'text', 'text': f'Here is a summary of your investigation so far: {summary}'}]
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
            'content': f'Summarize the following interaction between an AI agent and a user. Return the summary formatted as text, not as JSON: {json.dumps(messages)}'
        }
    ]

    completion_args = {
        'model': model_id,
        'messages': messages,
        # "frequency_penalty": args.frequency_penalty,
        # "max_tokens": 128,
        # "n": args.n,
        # "presence_penalty": args.presence_penalty,
        # "seed": args.seed,
        # "stop": args.stop,
        # "stream": args.stream,
        # "temperature": args.temperature,
        # "top_p": args.top_p,
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
