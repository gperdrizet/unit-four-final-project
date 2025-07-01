'''Unittests for agent tools.'''

import unittest
from functions.tools import (
    google_search,
    wikipedia_search,
    get_wikipedia_page,
    libretext_book_search,
    libretext_book_parser,
    libretext_chapter_parser
)


class TestGoogleSearch(unittest.TestCase):
    '''Tests for the google search tool.'''


    def setUp(self):

        google_search_query = 'Python programming language'
        self.search_results = google_search(google_search_query)


    def test_result_type(self):
        '''Search results should be a dictionary.'''

        self.assertIsInstance(self.search_results, dict)


    def test_result_length(self):
        '''Search results should contain 5 items.'''

        self.assertEqual(len(self.search_results), 10)


    def test_result_content(self):
        '''Each search result should contain three elements: title, link, and snippet.'''

        for result in self.search_results.values():
            self.assertIsInstance(result, dict)
            self.assertIn('title', result)
            self.assertIn('url', result)
            self.assertIn('description', result)
            self.assertIsInstance(result['title'], str)
            self.assertIsInstance(result['url'], str)
            self.assertIsInstance(result['description'], str)


class TestWikipediaSearch(unittest.TestCase):
    '''Tests for the wikipedia search tool.'''


    def setUp(self):

        wikipedia_search_query = 'Python programming language'
        self.search_results = wikipedia_search(wikipedia_search_query)


    def test_result_type(self):
        '''Search results should be a dictionary.'''

        self.assertIsInstance(self.search_results, dict)


    def test_result_length(self):
        '''Search results should contain 5 items.'''

        self.assertEqual(len(self.search_results), 5)


    def test_result_content(self):
        '''Each search result should contain three elements: title, link, and snippet.'''

        for _, result in self.search_results.items():
            self.assertIsInstance(result, dict)
            self.assertIn('title', result)
            self.assertIn('description', result)
            self.assertIsInstance(result['title'], str)
            self.assertIsInstance(result['description'], str)


class TestGetWikipediaPage(unittest.TestCase):
    '''Tests for the get_wikipedia_page tool.'''


    def setUp(self):

        self.page_content = get_wikipedia_page('Mercedes Sosa')


    def test_page_content_type(self):
        '''Page content should be a string.'''

        self.assertIsInstance(self.page_content, str)


    def test_page_content_not_empty(self):
        '''Page content should not be empty.'''

        self.assertTrue(len(self.page_content) > 0)


class TestLibretextBookSearch(unittest.TestCase):
    '''Tests for the libretext_book_search tool.'''

    def setUp(self):
        search_query = 'Introductory chemistry ck-12'
        self.search_results = libretext_book_search(search_query)

    def test_result_type(self):
        '''Search results should be a dictionary.'''
        self.assertIsInstance(self.search_results, dict)

    def test_no_error(self):
        '''Search results should not contain an error.'''
        self.assertNotIn('error', self.search_results)

    def test_result_content(self):
        '''Each search result should contain title, url, and description if results found.'''
        if len(self.search_results) > 0 and 'error' not in self.search_results:
            for result in self.search_results.values():
                self.assertIsInstance(result, dict)
                self.assertIn('title', result)
                self.assertIn('url', result)
                self.assertIn('description', result)
                self.assertIsInstance(result['title'], str)
                self.assertIsInstance(result['url'], str)
                self.assertIsInstance(result['description'], str)

    def test_first_result_exists(self):
        '''If results are found, the first result should have a meaningful title.'''
        if len(self.search_results) > 0 and 'error' not in self.search_results:
            first_result = next(iter(self.search_results.values()))
            self.assertTrue(len(first_result['title']) > 3)

    def test_result_urls_valid(self):
        '''URLs should be properly formatted if present.'''
        if len(self.search_results) > 0 and 'error' not in self.search_results:
            for result in self.search_results.values():
                if result['url']:  # Only test non-empty URLs
                    self.assertTrue(
                        result['url'].startswith('http://') or 
                        result['url'].startswith('https://') or
                        result['url'].startswith('/')
                    )


class TestLibretextBookParser(unittest.TestCase):
    '''Tests for the libretext_book_parser tool.'''

    def setUp(self):
        # Use a known LibreTexts book URL for testing
        book_url = 'https://chem.libretexts.org/Bookshelves/Introductory_Chemistry/Introductory_Chemistry_(CK-12)'
        self.parse_results = libretext_book_parser(book_url)

    def test_result_type(self):
        '''Parse results should be a dictionary.'''
        self.assertIsInstance(self.parse_results, dict)

    def test_no_error(self):
        '''Parse results should not contain an error.'''
        self.assertNotIn('error', self.parse_results)

    def test_result_content(self):
        '''Each chapter should contain title, url, and description if chapters found.'''
        if len(self.parse_results) > 0 and 'error' not in self.parse_results:
            for chapter in self.parse_results.values():
                self.assertIsInstance(chapter, dict)
                self.assertIn('title', chapter)
                self.assertIn('url', chapter)
                self.assertIn('description', chapter)
                self.assertIsInstance(chapter['title'], str)
                self.assertIsInstance(chapter['url'], str)
                self.assertIsInstance(chapter['description'], str)

    def test_chapters_found(self):
        '''Should find multiple chapters in a typical LibreTexts book.'''
        if 'error' not in self.parse_results:
            self.assertGreater(len(self.parse_results), 5)  # Expect at least several chapters

    def test_chapter_titles_meaningful(self):
        '''Chapter titles should be meaningful (not empty or too short).'''
        if len(self.parse_results) > 0 and 'error' not in self.parse_results:
            for chapter in self.parse_results.values():
                self.assertTrue(len(chapter['title']) > 2)

    def test_chapter_urls_valid(self):
        '''Chapter URLs should be properly formatted.'''
        if len(self.parse_results) > 0 and 'error' not in self.parse_results:
            for chapter in self.parse_results.values():
                if chapter['url']:  # Only test non-empty URLs
                    self.assertTrue(
                        chapter['url'].startswith('http://') or 
                        chapter['url'].startswith('https://') or
                        chapter['url'].startswith('/')
                    )


class TestLibretextChapterParser(unittest.TestCase):
    '''Tests for the libretext_chapter_parser tool.'''

    def setUp(self):
        # Use a known LibreTexts chapter URL for testing
        chapter_url = 'https://chem.libretexts.org/Bookshelves/Introductory_Chemistry/Introductory_Chemistry_(CK-12)/01%3A_Introduction_to_Chemistry'
        self.parse_results = libretext_chapter_parser(chapter_url)

    def test_result_type(self):
        '''Parse results should be a dictionary.'''
        self.assertIsInstance(self.parse_results, dict)

    def test_no_error(self):
        '''Parse results should not contain an error.'''
        self.assertNotIn('error', self.parse_results)

    def test_result_content(self):
        '''Each section should contain title, url, and description if sections found.'''
        if len(self.parse_results) > 0 and 'error' not in self.parse_results:
            for section in self.parse_results.values():
                self.assertIsInstance(section, dict)
                self.assertIn('title', section)
                self.assertIn('url', section)
                self.assertIn('description', section)
                self.assertIsInstance(section['title'], str)
                self.assertIsInstance(section['url'], str)
                self.assertIsInstance(section['description'], str)

    def test_sections_found(self):
        '''Should find multiple sections in a typical LibreTexts chapter.'''
        if 'error' not in self.parse_results:
            self.assertGreater(len(self.parse_results), 2)  # Expect at least a few sections

    def test_section_titles_meaningful(self):
        '''Section titles should be meaningful (not empty or too short).'''
        if len(self.parse_results) > 0 and 'error' not in self.parse_results:
            for section in self.parse_results.values():
                self.assertTrue(len(section['title']) > 2)

    def test_section_urls_valid(self):
        '''Section URLs should be properly formatted.'''
        if len(self.parse_results) > 0 and 'error' not in self.parse_results:
            for section in self.parse_results.values():
                if section['url']:  # Only test non-empty URLs
                    self.assertTrue(
                        section['url'].startswith('http://') or 
                        section['url'].startswith('https://') or
                        section['url'].startswith('/')
                    )

    def test_sections_have_descriptions(self):
        '''Most sections should have meaningful descriptions.'''
        if len(self.parse_results) > 0 and 'error' not in self.parse_results:
            sections_with_descriptions = sum(
                1 for section in self.parse_results.values() 
                if section['description'] and len(section['description']) > 10
            )
            # At least half the sections should have descriptions
            self.assertGreater(sections_with_descriptions, len(self.parse_results) // 2)

if __name__ == '__main__':
    unittest.main()
