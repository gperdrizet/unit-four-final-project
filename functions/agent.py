'''Agent definition for GAIA question answering system.'''

# Standard library
import logging

# Imports for agent creation
from smolagents import CodeAgent, VisitWebpageTool

from functions.tools import (
    google_search,
    wikipedia_search,
    get_wikipedia_page,
    libretext_book_search,
    get_libretext_book
)

from functions.agent_helper_functions import step_memory_cap, step_wait
from configuration import MODEL

# Get logger for this module
logger = logging.getLogger(__name__)

def create_agent():
    '''Creates agent for GAIA question answering system.'''

    # web_agent = CodeAgent(
    #     model=WORKER_MODEL,
    #     tools=[google_search, VisitWebpageTool()],
    #     additional_authorized_imports=['bs4.*', 'json'],
    #     step_callbacks=[step_memory_cap],
    #     name="web_agent",
    #     verbosity_level=5,
    #     max_steps=10,
    #     planning_interval=5,
    #     description="Web search agent for general queries and retrieving web pages as HTML",
    # )

    # wikipedia_agent = CodeAgent(
    #     model=WORKER_MODEL,
    #     tools=[wikipedia_search, get_wikipedia_page],
    #     additional_authorized_imports=['bs4.*', 'json'],
    #     step_callbacks=[step_memory_cap],
    #     name="wikipedia_agent",
    #     verbosity_level=5,
    #     max_steps=10,
    #     planning_interval=5,
    #     description="Wikipedia agent to search and retrieve Wikipedia pages as HTML",
    # )

    # libretext_agent = CodeAgent(
    #     model=WORKER_MODEL,
    #     tools=[libretext_book_search, get_libretext_book],
    #     additional_authorized_imports=['bs4.*', 'json'],
    #     step_callbacks=[step_memory_cap],
    #     name="libretext_agent",
    #     verbosity_level=5,
    #     max_steps=10,
    #     planning_interval=5,
    #     description="LibreText agent to search and retrieve content from academic textbooks books",
    # )

    # manager_agent = CodeAgent(
    #     model=MANAGER_MODEL,
    #     tools=[],
    #     managed_agents=[web_agent, wikipedia_agent, libretext_agent],
    #     additional_authorized_imports=['bs4.*', 'json'],
    #     planning_interval=2,
    #     verbosity_level=2,
    #     final_answer_checks=[check_reasoning],
    #     max_steps=20,
    # )

    agent = CodeAgent(
        model=MODEL,
        tools=[
            google_search,
            VisitWebpageTool(),
            wikipedia_search,
            get_wikipedia_page,
            libretext_book_search,
            get_libretext_book
        ],
        additional_authorized_imports=['bs4.*', 'json'],
        step_callbacks=[step_memory_cap, step_wait],
        name="GAIA_agent",
        verbosity_level=5,
        max_steps=20,
        planning_interval=5
    )

    return agent
