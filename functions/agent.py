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
        "Qwen/Qwen2.5-Coder-32B-Instruct",
        provider="hf-inference",
        max_tokens=8096
    )

    tools = [
        wikipedia_search,
        get_wikipedia_page,
        google_search,
        VisitWebpageTool()
    ]

    agent = CodeAgent(
        model=model,
        tools=tools,
        additional_authorized_imports=['bs4.*', 'json'],
        name="GAIA_agent",
        verbosity_level=1,
        max_steps=20,
        planning_interval=5,
        description="GAIA agent for question answering"
    )


    return agent
