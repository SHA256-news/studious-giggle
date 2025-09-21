#!/usr/bin/env python3
"""
Test to ensure filter_bitcoin_only_articles function signature is protected
from breaking changes that would affect calling code.
"""

import unittest
from crypto_filter import filter_bitcoin_only_articles


class TestFunctionSignatureProtection(unittest.TestCase):
    """Test class to protect against breaking changes in function signatures"""
    
    def test_filter_bitcoin_only_articles_returns_tuple(self):
        """Test that filter_bitcoin_only_articles ALWAYS returns a tuple with 3 elements"""
        test_articles = [
            {
                'title': 'Bitcoin Mining Facility Opens in Texas',
                'body': 'A new Bitcoin mining facility has opened.',
                'url': 'https://example.com/bitcoin-news',
                'uri': 'test-1'
            },
            {
                'title': 'Ethereum Mining Gets Harder',
                'body': 'Ethereum mining difficulty has increased.',
                'url': 'https://example.com/eth-news',
                'uri': 'test-2'
            }
        ]
        
        result = filter_bitcoin_only_articles(test_articles)
        
        # Critical: Must be a tuple
        self.assertIsInstance(result, tuple, 
                            "filter_bitcoin_only_articles MUST return a tuple, not a list or other type")
        
        # Critical: Must have exactly 3 elements
        self.assertEqual(len(result), 3, 
                        "filter_bitcoin_only_articles MUST return exactly 3 elements")
        
        # Verify tuple unpacking works (this is what calling code expects)
        filtered_articles, excluded_count, excluded_details = result
        
        # Verify types of returned elements
        self.assertIsInstance(filtered_articles, list, 
                            "First element (filtered_articles) must be a list")
        self.assertIsInstance(excluded_count, int, 
                            "Second element (excluded_count) must be an int")
        self.assertIsInstance(excluded_details, list, 
                            "Third element (excluded_details) must be a list")
    
    def test_filter_bitcoin_only_articles_empty_input_returns_tuple(self):
        """Test that function returns tuple even with empty input"""
        result = filter_bitcoin_only_articles([])
        
        # Must still be a tuple with 3 elements
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        
        # Should be empty values but correct types
        filtered_articles, excluded_count, excluded_details = result
        self.assertEqual(filtered_articles, [])
        self.assertEqual(excluded_count, 0)
        self.assertEqual(excluded_details, [])
    
    def test_filter_bitcoin_only_articles_none_input_returns_tuple(self):
        """Test that function returns tuple even with None input"""
        result = filter_bitcoin_only_articles(None)
        
        # Must still be a tuple with 3 elements  
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
    
    def test_calling_code_compatibility(self):
        """Test that the function works with actual calling patterns used in the codebase"""
        test_articles = [
            {'title': 'Bitcoin Mining News', 'body': 'Bitcoin mining content', 'url': 'test.com'},
            {'title': 'Ethereum News', 'body': 'Ethereum content', 'url': 'test2.com'}
        ]
        
        # This is how api_clients.py calls the function
        filtered_articles, excluded_count, excluded_details = filter_bitcoin_only_articles(test_articles)
        
        # Verify the expected behavior
        self.assertEqual(len(filtered_articles), 1)  # Only Bitcoin article
        self.assertEqual(excluded_count, 1)  # One Ethereum article excluded
        self.assertEqual(len(excluded_details), 1)  # Details for one excluded article
        
        # Verify excluded details structure
        excluded_detail = excluded_details[0]
        self.assertIn('title', excluded_detail)
        self.assertIn('url', excluded_detail)
        self.assertIn('found_in_title', excluded_detail)
        self.assertIn('found_in_body', excluded_detail)


def main():
    """Run the signature protection tests"""
    print("=" * 80)
    print("FUNCTION SIGNATURE PROTECTION TESTS")
    print("Ensuring filter_bitcoin_only_articles maintains tuple return format")
    print("=" * 80)
    
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()