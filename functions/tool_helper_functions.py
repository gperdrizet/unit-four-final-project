'''Helper functions for GAIA question answering agent tools.'''

import time
import logging
import requests
from bs4 import BeautifulSoup

# Get logger for this module
logger = logging.getLogger(__name__)


def libretext_book_parser(url: str) -> dict:
    """
    Parse the content of a LibreTexts book and return table of contents as JSON.
    
    Args:
        url (str): The URL of the LibreTexts book page.
        
    Returns:
        dict: A dictionary containing the table of contents in the following format.
        {0: {'title': str, 'url': str, 'description': str}, ...}
    """

    logger.info('Parsing LibreTexts book: %s', url)

    # Set up headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' +
            '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        # Fetch the book page
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for the table of contents structure
        # LibreTexts books typically use li elements with class 'mt-sortable-listing'
        chapter_listings = soup.find_all('li', class_='mt-sortable-listing')

        logger.info('Found %d potential chapter listings', len(chapter_listings))

        parsed_chapters = {}
        chapter_count = 0

        for listing in chapter_listings:
            # Extract the link element
            link = listing.find('a', class_='mt-sortable-listing-link')

            if link:
                # Extract title from the span with class 'mt-sortable-listing-title'
                title_span = link.find('span', class_='mt-sortable-listing-title')
                title = title_span.get_text(strip=True) if title_span else ''

                # Extract URL from href attribute
                chapter_url = link.get('href', '')

                # Extract description from the title attribute of the link
                description = link.get('title', '')

                # Clean up description - remove the title prefix if it appears
                if description and title and description.startswith(title):
                    description = description[len(title):].strip()
                    if description.startswith(':'):
                        description = description[1:].strip()

                # Only add meaningful chapters (skip empty titles or very short ones)
                if title and len(title) > 2:
                    parsed_chapters[chapter_count] = {
                        'title': title,
                        'url': chapter_url,
                        'description': description
                    }

                    logger.debug('Extracted chapter %d: title="%s", url="%s"', 
                               chapter_count, title, chapter_url)
                    chapter_count += 1

        logger.info('Successfully extracted %d chapters from book', len(parsed_chapters))
        return parsed_chapters

    except requests.exceptions.RequestException as e:
        logger.error('Request error while fetching book page: %s', str(e))
        return {'error': f'Request error: {str(e)}'}

    except Exception as e: # pylint:disable=broad-exception-caught
        logger.error('Unexpected error in book parser: %s', str(e))
        return {'error': f'Unexpected error: {str(e)}'}


def libretext_chapter_parser(url: str) -> dict:
    """
    Parse the content of a LibreTexts chapter and return section headings as JSON.
    
    Args:
        url (str): The URL of the LibreTexts chapter page.
        
    Returns:
        dict: A dictionary containing the section headings in the following format.
        {0: {'title': str, 'url': str, 'description': str}, ...}
    """

    logger.info('Parsing LibreTexts chapter: %s', url)

    # Set up headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' +
            '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        # Fetch the chapter page
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for the section structure
        # LibreTexts chapters typically use li elements with class 'mt-list-topics'
        section_listings = soup.find_all('li', class_='mt-list-topics')

        logger.info('Found %d potential section listings', len(section_listings))

        parsed_sections = {}
        section_count = 0

        for listing in section_listings:
            # Look for the detailed listing structure
            dl_element = listing.find('dl', class_='mt-listing-detailed')

            if dl_element:
                # Extract title and URL from the dt element
                dt_element = dl_element.find('dt', class_='mt-listing-detailed-title')
                dd_element = dl_element.find('dd', class_='mt-listing-detailed-overview')

                if dt_element:
                    # Find the anchor tag within the dt element
                    link = dt_element.find('a')

                    if link:
                        # Extract title from the link text
                        title = link.get_text(strip=True)

                        # Extract URL from href attribute
                        section_url = link.get('href', '')

                        # Extract description from the dd element
                        description = ''
                        if dd_element:
                            description = dd_element.get_text(strip=True)

                        # Only add meaningful sections (skip empty titles or very short ones)
                        if title and len(title) > 2:
                            parsed_sections[section_count] = {
                                'title': title,
                                'url': section_url,
                                'description': description
                            }

                            logger.debug('Extracted section %d: title="%s", url="%s"', 
                                       section_count, title, section_url)
                            section_count += 1

        logger.info('Successfully extracted %d sections from chapter', len(parsed_sections))
        return parsed_sections

    except requests.exceptions.RequestException as e:
        logger.error('Request error while fetching chapter page: %s', str(e))
        return {'error': f'Request error: {str(e)}'}

    except Exception as e:  # pylint:disable=broad-exception-caught
        logger.error('Unexpected error in chapter parser: %s', str(e))
        return {'error': f'Unexpected error: {str(e)}'}


def save_libretext_book_as_markdown(book_data: dict, filename: str = None, source_url: str = None) -> str:
    """
    Save a complete LibreTexts book dictionary as a markdown formatted file.
    
    Args:
        book_data (dict): The complete book data dictionary from get_libretext_book().
        filename (str, optional): The filename to save the markdown. If not provided,
                                 will generate based on book title.
        source_url (str, optional): The original URL of the book for reference in the markdown.
        
    Returns:
        str: A message indicating success or failure with the filename used.
    """

    logger.info('Saving LibreTexts book as markdown')

    if 'error' in book_data:
        error_msg = f"Cannot save book with error: {book_data['error']}"
        logger.error(error_msg)
        return error_msg

    # Generate filename if not provided
    if filename is None:
        book_title = book_data.get('title', 'LibreTexts_Book')
        # Clean up the title for use as filename
        safe_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        filename = f"{safe_title}.md"

    # Ensure .md extension
    if not filename.endswith('.md'):
        filename += '.md'

    try:
        # Format the book data as markdown
        markdown_content = []

        # Book title
        book_title = book_data.get('title', 'LibreTexts Book')
        markdown_content.append(f"# {book_title}\n")
        if source_url:
            markdown_content.append(f"*Extracted from: {source_url}*\n")
        markdown_content.append(f"*Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n")

        # Table of contents
        chapters = book_data.get('chapters', {})
        if chapters:
            markdown_content.append("## Table of Contents\n")
            for chapter_title in chapters.keys():
                # Create anchor link for the chapter
                anchor = chapter_title.lower().replace(' ', '-').replace(':', '').replace('(', '').replace(')', '')
                markdown_content.append(f"- [{chapter_title}](#{anchor})\n")
            markdown_content.append("\n---\n\n")

        # Chapter content
        for chapter_title, chapter_data in chapters.items():
            # Chapter heading
            markdown_content.append(f"## {chapter_title}\n\n")

            sections = chapter_data.get('sections', {})

            if not sections:
                markdown_content.append("*No sections found for this chapter.*\n\n")
                continue

            # Section content
            for section_title, section_data in sections.items():
                # Section heading
                markdown_content.append(f"### {section_title}\n\n")

                # Section URL
                section_url = section_data.get('Section url', '')
                if section_url:
                    markdown_content.append(f"**URL:** [{section_url}]({section_url})\n\n")

                # Section summary
                section_summary = section_data.get('Section summary', '')
                if section_summary:
                    markdown_content.append(f"{section_summary}\n\n")
                else:
                    markdown_content.append("*No summary available.*\n\n")

                markdown_content.append("---\n\n")

        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(markdown_content)

        success_msg = f"Successfully saved LibreTexts book as markdown file: {filename}"
        logger.info(success_msg)
        return success_msg

    except Exception as e:  # pylint:disable=broad-exception-caught
        error_msg = f"Error saving markdown file: {str(e)}"
        logger.error(error_msg)
        return error_msg
