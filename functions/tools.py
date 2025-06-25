'''Tools for GAIA question answering agent.'''

from smolagents import tool
from googlesearch import search

@tool
def google_search(query: str) -> str:
    """
    Perform a Google search and return the top 10 results.
    
    Args:
        query (str): The search query.
        
    Returns:
        str: The URLs of the top search results, separated by newlines.
    """

    results = list(search(query, num_results=10, advanced=True))

    return results
