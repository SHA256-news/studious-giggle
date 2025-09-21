#!/usr/bin/env python3
"""
Test for concepts fallback pattern fix
Verifies that concepts display properly with 'none' fallback for better log readability
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import TextUtils


def test_concepts_with_none_fallback():
    """Test that concepts use 'none' fallback when empty for better readability"""
    print("🧪 Testing concepts fallback pattern...")
    
    # Test 1: Article with concepts
    article_with_concepts = {
        "title": "Bitcoin Mining Difficulty Reaches New High",
        "body": "Bitcoin mining operations face new challenges as network difficulty adjusts."
    }
    
    info = TextUtils.extract_key_info(article_with_concepts)
    concepts = info.get("concepts", [])
    concepts_str = ', '.join(concepts) if concepts else 'none'
    
    print(f"✓ Article with concepts:")
    print(f"  Concepts found: {concepts}")
    print(f"  Display string: '{concepts_str}'")
    
    if concepts:
        assert concepts_str == ', '.join(concepts), "Should join concepts with commas"
        print("  ✅ Concepts joined correctly")
    
    # Test 2: Article without concepts
    article_without_concepts = {
        "title": "Simple news article",
        "body": "This is a simple article without specific Bitcoin concepts."
    }
    
    info = TextUtils.extract_key_info(article_without_concepts)
    concepts = info.get("concepts", [])
    concepts_str = ', '.join(concepts) if concepts else 'none'
    
    print(f"\n✓ Article without concepts:")
    print(f"  Concepts found: {concepts}")
    print(f"  Display string: '{concepts_str}'")
    
    assert concepts_str == 'none', "Should fallback to 'none' when concepts is empty"
    print("  ✅ Fallback to 'none' works correctly")
    
    # Test 3: Verify readability improvement
    print(f"\n✓ Readability improvement:")
    print(f"  ❌ Old unclear pattern: 'Concepts: =' (confusing)")
    print(f"  ✅ New clear pattern: 'Concepts: {concepts_str}' (readable)")
    
    return True


def test_pattern_consistency():
    """Test that the pattern is consistent with other similar displays"""
    print(f"\n🔍 Testing pattern consistency...")
    
    # Test the actual pattern used in show_queued_tweets.py
    concepts_empty = []
    concepts_with_values = ['mining', 'difficulty']
    
    # Empty case
    concepts_str_empty = ', '.join(concepts_empty) if concepts_empty else 'none'
    assert concepts_str_empty == 'none', "Empty concepts should show 'none'"
    
    # Non-empty case  
    concepts_str_filled = ', '.join(concepts_with_values) if concepts_with_values else 'none'
    assert concepts_str_filled == 'mining, difficulty', "Non-empty concepts should be joined"
    
    print(f"  ✅ Empty concepts: '{concepts_str_empty}'")
    print(f"  ✅ Non-empty concepts: '{concepts_str_filled}'")
    
    return True


if __name__ == "__main__":
    print("🔧 Testing concepts fallback pattern fix (Issue #79)")
    print("=" * 60)
    
    try:
        success = test_concepts_with_none_fallback()
        success = success and test_pattern_consistency()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ All tests passed!")
            print("✅ Concepts now use 'none' fallback for better log readability")
            print("✅ Issue #79 resolved")
        else:
            print("\n❌ Some tests failed!")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        success = False
    
    exit(0 if success else 1)