'''Agent definition for GAIA question answering system.'''

# Imports for agent creation
from smolagents import CodeAgent, ToolCallingAgent, InferenceClientModel, VisitWebpageTool
from functions.tools import (
    google_search,
    wikipedia_search,
    get_wikipedia_page
)

def create_agent():
    '''Creates agent for GAIA question answering system.'''

    model = InferenceClientModel(
        "Qwen/Qwen2.5-Coder-32B-Instruct", provider="together"
    )

    web_agent_tools = [
        google_search,
        VisitWebpageTool()
    ]

    web_agent = CodeAgent(
        model=model,
        tools=web_agent_tools,
        name="web_agent",
        description="Browses the web to find information",
        verbosity_level=1,
        max_steps=10,
    )

    wikipedia_agent_tools = [
        wikipedia_search,
        get_wikipedia_page
    ]

    wikipedia_agent = CodeAgent(
        model=model,
        tools=wikipedia_agent_tools,
        additional_authorized_imports=['bs4.*'],
        name="wikipedia_agent",
        description="Search Wikipedia and retrieve pages",
        verbosity_level=1,
        max_steps=10
    )

    manager_agent = CodeAgent(
        model=model,
        tools=[],
        additional_authorized_imports=['bs4.*'],
        name="manager_agent",
        description="Manages the workflow of other agents",
        managed_agents=[web_agent, wikipedia_agent],
        planning_interval=1,
        verbosity_level=2,
        max_steps=15,
    )

    manager_agent.visualize()

    return manager_agent
