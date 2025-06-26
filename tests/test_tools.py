'''Unittests for agent tools.'''

import unittest
from functions.tools import (
    google_search,
    wikipedia_search,
    get_wikipedia_page
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

        self.assertEqual(len(self.search_results), 5)


    def test_result_content(self):
        '''Each search result should contain three elements: title, link, and snippet.'''

        for _, result in self.search_results.items():
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
