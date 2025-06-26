'''Unittests for agent tools.'''

import unittest
import googlesearch
from functions.tools import google_search


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

        print(type(self.search_results[1]))

        for _, result in self.search_results.items():
            self.assertIsInstance(result, dict)
            self.assertIn('title', result)
            self.assertIn('url', result)
            self.assertIn('description', result)
            self.assertIsInstance(result['title'], str)
            self.assertIsInstance(result['url'], str)
            self.assertIsInstance(result['description'], str)
