#!/usr/bin/env python3
"""
Test to reproduce the specific None handling issue
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_none_title_issue():
    """Test the specific None title issue"""
    print("Testing None title issue...")
    
    # Simulate the problematic code from create_enhanced_tweet_text
    title = None  # This is what happens when article.get("title", "") returns None
    
    try:
        # This is the problematic line from utils.py
        if not title or not title.strip():
            print("✗ This should fail with AttributeError")
        return False
    except AttributeError as e:
        print(f"✓ Found the issue: {e}")
        return True
    except Exception as e:
        print(f"? Unexpected error: {e}")
        return False

def test_fix_none_title():
    """Test the fix for None title issue"""
    print("Testing fix for None title issue...")
    
    title = None
    
    try:
        # Fixed version: handle None properly
        if not title or (title and not title.strip()):
            print("✓ Fixed version handles None correctly")
            return True
        return False
    except Exception as e:
        print(f"✗ Fixed version failed: {e}")
        return False

def test_real_function_with_none():
    """Test the real function with None title"""
    print("Testing real function with None title...")
    
    try:
        from utils import TextUtils
        
        # Test article with None title
        article = {"title": None, "url": "https://example.com", "uri": "test-uri"}
        
        result = TextUtils.create_enhanced_tweet_text(article)
        print(f"✓ Function completed, result: {result[:50]}...")
        return True
        
    except AttributeError as e:
        if "NoneType" in str(e) and "strip" in str(e):
            print(f"✓ Found the exact issue: {e}")
            return True
        print(f"? Different AttributeError: {e}")
        return False
    except Exception as e:
        print(f"? Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Testing None title handling issue...")
    print("=" * 50)
    
    success1 = test_none_title_issue()
    success2 = test_fix_none_title()
    success3 = test_real_function_with_none()
    
    print(f"\nResults:")
    print(f"- None.strip() issue: {'FOUND' if success1 else 'NOT FOUND'}")
    print(f"- Fix works: {'YES' if success2 else 'NO'}")
    print(f"- Real function issue: {'FOUND' if success3 else 'NOT FOUND'}")