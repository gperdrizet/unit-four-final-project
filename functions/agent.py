'''Agent definition for GAIA question answering system.'''

# Imports for agent creation
from smolagents import CodeAgent, DuckDuckGoSearchTool, InferenceClientModel, VisitWebpageTool, Tool
from langchain_community.agent_toolkits.load_tools import load_tools

def create_agent():
    '''Creates agent for GAIA question answering system.'''

    wikipedia_tool = Tool.from_langchain(
        load_tools(["wikipedia"])[0]
    )

    model = InferenceClientModel(
        "Qwen/Qwen2.5-Coder-32B-Instruct"
    )

    agent = CodeAgent(
        tools=[wikipedia_tool, DuckDuckGoSearchTool(), VisitWebpageTool()],
        model=model
    )

    return agent
