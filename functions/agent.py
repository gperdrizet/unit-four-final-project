'''Agent definition for GAIA question answering system.'''

# Imports for agent creation
from smolagents import CodeAgent, InferenceClientModel, VisitWebpageTool
from functions.tools import (
    google_search,
    wikipedia_search,
    get_wikipedia_page
)

def create_agent():
    '''Creates agent for GAIA question answering system.'''

    model = InferenceClientModel(
        # max_tokens=8096,
        # temperature=0.5,
        model_id='Qwen/Qwen2.5-Coder-32B-Instruct',
        provider='together'
        # custom_role_conversions=None
    )

    tools = [
        google_search,
        wikipedia_search,
        get_wikipedia_page,
        VisitWebpageTool()
    ]

    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=20,
        planning_interval=2,
        additional_authorized_imports=['bs4.*']
    )

    return agent
