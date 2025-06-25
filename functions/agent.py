'''Agent definition for GAIA question answering system.'''

# Imports for agent creation
from smolagents import CodeAgent, InferenceClientModel, VisitWebpageTool, Tool
from langchain_community.agent_toolkits.load_tools import load_tools
from functions.tools import google_search

def create_agent():
    '''Creates agent for GAIA question answering system.'''

    wikipedia = Tool.from_langchain(
        load_tools(["wikipedia"])[0]
    )

    model = InferenceClientModel(
        "Qwen/Qwen2.5-Coder-32B-Instruct"
    )

    agent = CodeAgent(
        tools=[wikipedia, google_search, VisitWebpageTool()],
        model=model
    )

    return agent
