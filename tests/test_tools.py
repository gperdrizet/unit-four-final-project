'''Unittests for agent tools.'''

import unittest
from functions.tools import (
    google_search,
    wikipedia_search,
    get_wikipedia_page,
    libretext_book_search
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
