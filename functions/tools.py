'''Tools for GAIA question answering agent.'''

import time
import logging
import requests
from smolagents import tool
from googlesearch import search
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from functions.tool_helper_functions import (
    libretext_book_parser,
    libretext_chapter_parser,
    save_libretext_book_as_markdown,
    WikipediaFetcher
)

# Get logger for this module
logger = logging.getLogger(__name__)


@tool
def google_search(query: str) -> dict:
    """
    Perform a Google search and return the top 10 results.
    
    Args:
        query (str): The search query.
        
    Returns:
        dict: A dictionary containing the search results in the following format.
        {0: {'title': str, 'url': str, 'description': str}, ...}
    """

    # Run the query
    results = list(search(query, num_results=10, advanced=True))

    # Parse and format the results
    parsed_results = {}

    for i, result in enumerate(results):

        parsed_results[i] = {
            'title': result.title,
            'url': result.url,
            'description': result.description
        }

    return parsed_results


@tool
def wikipedia_search(query: str) -> dict:
    """
    Perform a search for wikipedia pages and return the top 5 results.
    
    Args:
        query (str): The search query.
        
    Returns:
        dict: A dictionary containing the search results in the following format.
        {0: {'title': str, 'description': str}, ...}
    """

    repo_url = 'https://github.com/gperdrizet/unit-four-final-project'

    language_code = 'en'
    number_of_results = 5
    headers = {
        'User-Agent': f'HuggingFace Agents course final project ({repo_url})'
    }

    base_url = 'https://api.wikimedia.org/core/v1/wikipedia/'
    endpoint = '/search/page'
    url = base_url + language_code + endpoint
    parameters = {'q': query, 'limit': number_of_results}
    response = requests.get(url, headers=headers, params=parameters, timeout=15)

    if response.status_code == 200:
        results = response.json().get('pages', [])
        parsed_results = {}

    else:
        return f"Error: Unable to retrieve page. Status code {response.status_code}"

    for i, result in enumerate(results):

        parsed_results[i] = {
            'title': result.get('title', None),
            'description': result.get('description', None)
        }

    return parsed_results


@tool
def get_wikipedia_page(query: str) -> str:
    """
    Get the content of a Wikipedia page as HTML. Use this tool when trying to
    retrieve information from a Wikipedia page or article.

    Args:
        query (str): The title of the Wikipedia page.
        
    Returns:
        str: The HTML content of the Wikipedia page.
    """

    fetcher = WikipediaFetcher()
    html_result = fetcher.fetch(query.replace(' ', '_'))

    content = html_result['content']

    content = content.split(
        '<div class="mw-heading mw-heading2"><h2 id="Further_reading">Further reading</h2></div>'
    )[0]

    content = content.split(
        '<div class="mw-heading mw-heading2"><h2 id="References">References</h2></div>'
    )[0]

    return content


@tool
def libretext_book_search(query: str) -> dict:
    """
    Search for LibreTexts books using Selenium to handle JavaScript-rendered content.
    
    Args:
        query (str): The search query.
        
    Returns:
        dict: A dictionary containing the search results in the following format.
        {0: {'title': str, 'url': str, 'description': str}, ...}
    """

    # Configure Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = None
    try:
        # Initialize the Chrome driver
        driver = webdriver.Chrome(options=chrome_options)

        # Construct search URL
        search_url = 'https://chem.libretexts.org/Special:Search'
        params = {
            'qid': '',
            'fpid': '230',
            'fpth': '',
            'query': query
        }

        # Build URL with parameters
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{search_url}?{param_string}"

        logger.info('Selenium search URL: %s', full_url)

        # Navigate to the search page
        driver.get(full_url)

        # Wait for the search results to load
        # Wait for either search results or an indication that search is complete
        wait = WebDriverWait(driver, 15)

        try:
            # Wait for the search results container to be present and have content
            # or for a specific search result element to appear
            _ = wait.until(
                EC.presence_of_element_located((By.ID, "mt-search-spblls"))
            )

            # Give additional time for JavaScript to populate results
            time.sleep(3)

            # Get the page source after JavaScript execution
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Look for search results using multiple possible selectors
            search_info_divs = soup.find_all('div', class_='mt-search-information')

            # If no results with that class, try other common search result patterns
            if not search_info_divs:
                # Try alternative selectors that might be used for search results
                search_info_divs = soup.find_all('div', class_='search-result')
                if not search_info_divs:
                    search_info_divs = soup.find_all('div', class_='result')
                if not search_info_divs:
                    # Look for any divs within the search results container
                    results_container = soup.find('div', id='mt-search-spblls')
                    if results_container:
                        search_info_divs = results_container.find_all('div', recursive=False)

            logger.info('Found %d potential search result divs', len(search_info_divs))

            # Parse the search results
            parsed_results = {}
            result_count = 0

            for div in search_info_divs:
                # Try to extract title and URL from various possible structures
                title = None
                url = None
                summary = None

                # Look for title in anchor tags
                title_link = div.find('a')
                if title_link:
                    title = title_link.get_text(strip=True)
                    url = title_link.get('href', '')

                    # Make URL absolute if it's relative
                    if url and url.startswith('/'):
                        url = 'https://chem.libretexts.org' + url

                # Look for description/summary text
                # Try multiple approaches to find descriptive text
                text_elements = div.find_all(['p', 'span', 'div'])
                for element in text_elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 20 and not title or text != title:
                        summary = text
                        break

                # Only add to results if we have at least a title
                if title and len(title) > 3:  # Ensure title is meaningful
                    parsed_results[result_count] = {
                        'title': title,
                        'url': url or '',
                        'description': summary or ''
                    }

                    logger.debug(
                        'Extracted result %d: title="%s", url="%s"',
                        result_count,
                        title,
                        url
                    )

                    result_count += 1

            logger.info('Successfully extracted %d search results', len(parsed_results))
            return parsed_results

        except TimeoutException:
            logger.error('Timeout waiting for search results to load')
            return {'error': 'Timeout waiting for search results to load'}

    except WebDriverException as e:
        logger.error('WebDriver error: %s', str(e))
        return {'error': f'WebDriver error: {str(e)}'}

    except Exception as e: # pylint:disable=broad-exception-caught
        logger.error('Unexpected error in Selenium search: %s', str(e))
        return {'error': f'Unexpected error: {str(e)}'}

    finally:
        # Always clean up the driver
        if driver:
            try:
                driver.quit()
            except Exception as e: # pylint:disable=broad-exception-caught
                logger.warning('Error closing driver: %s', str(e))


@tool
def get_libretext_book(url: str) -> dict:
    """
    Get the complete content of a LibreTexts book including all chapters and sections.
    
    Args:
        url (str): The URL of the LibreTexts book page.
        
    Returns:
        dict: A dictionary containing the complete book structure in the following format.
        {
            'title': 'book title string',
            'chapters': {
                'Chapter title': {
                    'sections': {
                        'Section title': {
                            'Section summary': 'Section summary string',
                            'Section url': 'https://example.com/section-url',
                        },
                        ...
                    }
                },
                ...
            }
        }
    """

    logger.info('Getting complete LibreTexts book: %s', url)

    # First, get the book structure (chapters)
    book_data = libretext_book_parser(url)

    if 'error' in book_data:
        logger.error('Failed to parse book structure: %s', book_data['error'])
        return book_data

    # Extract book title from URL or use a default
    book_title = url.split('/')[-1].replace('%3A', ':').replace('_', ' ')
    if '(' in book_title:
        book_title = book_title.split('(')[0].strip()

    # Initialize the complete book structure
    complete_book = {
        'title': book_title,
        'chapters': {}
    }

    logger.info('Found %d chapters to process', len(book_data))

    # Process each chapter
    for chapter_info in book_data.values():
        chapter_title = chapter_info['title']
        chapter_url = chapter_info['url']

        logger.info('Processing chapter: %s', chapter_title)

        # Get sections for this chapter
        sections_data = libretext_chapter_parser(chapter_url)

        # Initialize chapter structure
        complete_book['chapters'][chapter_title] = {
            'sections': {}
        }

        if 'error' in sections_data:
            logger.warning('Failed to parse sections for chapter "%s": %s', 
                         chapter_title, sections_data['error'])
            complete_book['chapters'][chapter_title]['sections']['Error'] = {
                'Section summary': f"Failed to parse sections: {sections_data['error']}",
                'Section url': chapter_url
            }
        else:
            # Process each section
            for section_info in sections_data.values():
                section_title = section_info['title']
                section_url = section_info['url']
                section_description = section_info['description']

                complete_book['chapters'][chapter_title]['sections'][section_title] = {
                    'Section summary': section_description,
                    'Section url': section_url
                }

                logger.debug('Added section: %s', section_title)

            logger.info('Successfully processed %d sections for chapter "%s"',
                       len(sections_data), chapter_title)

    logger.info('Successfully compiled complete book with %d chapters',
               len(complete_book['chapters']))

    save_libretext_book_as_markdown(complete_book, filename=f"{book_title}.md", source_url=url)

    return complete_book

