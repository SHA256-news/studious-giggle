#!/usr/bin/env python3
"""
Test to reproduce the None handling issue
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_filter import filter_bitcoin_only_articles
from diagnose_bot import analyze_why_no_posts

def test_none_articles_crypto_filter():
    """Test crypto filter with None articles"""
    print("Testing crypto filter with None articles...")
    try:
        result = filter_bitcoin_only_articles(None)
        print(f"✓ filter_bitcoin_only_articles(None) returned: {result}")
        return True
    except Exception as e:
        print(f"✗ filter_bitcoin_only_articles(None) failed: {e}")
        return False

def test_none_articles_diagnose():
    """Test diagnose function with None articles"""
    print("Testing diagnose function with None articles...")
    try:
        # This should not crash
        analyze_why_no_posts(None, {"posted_uris": []})
        print("✓ analyze_why_no_posts(None, ...) completed without error")
        return True
    except Exception as e:
        print(f"✗ analyze_why_no_posts(None, ...) failed: {e}")
        return False

def test_simulated_bot_run_with_none():
    """Test simulated bot scenario where articles might be None"""
    print("Testing simulated bot run scenario with None articles...")
    try:
        articles = None
        
        # This is the pattern used in bot.py
        if not articles:
            print("  Empty articles check passed")
            # But then the code continues with len(articles) and iteration
            # This should fail if articles is None
            print(f"  len(articles) = {len(articles)}")  # This should fail
            
        return False  # Should not reach here
    except Exception as e:
        print(f"✗ Simulated bot run failed as expected: {e}")
        return True  # This is expected to fail

if __name__ == "__main__":
    print("Testing None handling issue...")
    print("=" * 50)
    
    success1 = test_none_articles_crypto_filter()
    success2 = test_none_articles_diagnose()
    success3 = test_simulated_bot_run_with_none()
    
    print("\nResults:")
    print(f"- crypto_filter with None: {'PASS' if success1 else 'FAIL'}")
    print(f"- diagnose with None: {'PASS' if success2 else 'FAIL'}")
    print(f"- simulated bot with None: {'PASS' if success3 else 'FAIL'}")
    
    if success1 and success2:
        print("\n✓ Current implementations handle None correctly")
    else:
        print("\n✗ Some functions don't handle None correctly")