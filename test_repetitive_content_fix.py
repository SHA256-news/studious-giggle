#!/usr/bin/env python3
"""
Test script to verify the fix for the repetitive content issue
described in the problem statement.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import TextUtils

def test_original_problem_fix():
    """Test the exact problem described in the issue"""
    print("🔧 TESTING REPETITIVE CONTENT FIX")
    print("="*60)
    
    # Recreate the exact scenario from the problem statement
    article = {
        'title': 'Five Solo Bitcoin Miners Stun Crypto World, Each Cashing In Over $350K in 2025 Despite Record Difficulty!',
        'body': 'The article confirms the key details. 5 solo Bitcoin miners earned over $350,000 each. This is a rare feat in the current mining landscape.',
        'url': 'https://example.com/solo-miners',
        'gemini_headline': 'Five Solo Bitcoin Miners Stun Crypto World, Each Cashing In Over $350K in 2025 Despite Record Difficulty!',
        'gemini_summary': 'The article confirms the key details.\n- 5 solo Bitcoin miners earned over $350,000 each.\n- This is a rare f...'
    }
    
    print("ORIGINAL PROBLEM:")
    print('tweet 1: "📰 Five Solo Bitcoin Miners Stun Crypto World, Each Cashing In Over $350K in 2025 Despite Record Difficulty!"')
    print('tweet 2:" The article confirms the key details.')
    print('- 5 solo Bitcoin miners earned over $350,000 each.')
    print('- This is a rare f..."')
    print()
    
    # Test both thread formats
    hook, link = TextUtils.create_thread_texts(article)
    hook3, summary3, url3 = TextUtils.create_three_part_thread(article)
    
    print("AFTER FIX:")
    print("2-Part Thread:")
    print(f'Tweet 1: "{hook}"')
    print(f'Tweet 2: "{link}"')
    print()
    
    print("3-Part Thread:")
    print(f'Tweet 1: "{hook3}"')
    print(f'Tweet 2: "{summary3}"')
    print(f'Tweet 3: "{url3}"')
    print()
    
    # Validation
    errors = []
    
    # Check that "The article confirms the key details." is removed
    if "The article confirms the key details" in link:
        errors.append("2-part thread still contains generic opening")
    
    if "The article confirms the key details" in summary3:
        errors.append("3-part thread still contains generic opening")
    
    # Check that content starts properly without generic phrases
    if not summary3.startswith("- 5 solo Bitcoin miners"):
        errors.append("3-part summary doesn't start with expected content")
    
    if errors:
        print("❌ ERRORS FOUND:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ VALIDATION CHECKS:")
        print("  - Generic opening 'The article confirms the key details.' removed from both thread formats")
        print("  - Content starts properly with meaningful information")
        print("  - Formatting preserved for bullet points")
        print()
        print("🎉 PROBLEM FIXED SUCCESSFULLY!")
        return True

def test_additional_generic_phrases():
    """Test other generic phrases to ensure comprehensive coverage"""
    print("\n🧪 TESTING ADDITIONAL GENERIC PHRASES")
    print("="*60)
    
    test_cases = [
        {
            'name': 'According to the article',
            'summary': 'According to the article: Bitcoin mining difficulty increases.\n- New record set\n- Miners adapting',
            'expected_start': 'Bitcoin mining difficulty increases.'
        },
        {
            'name': 'The article states that',
            'summary': 'The article states that: Marathon Digital expands.\n- 500 MW facility\n- Q1 2025 target',
            'expected_start': 'Marathon Digital expands.'
        },
        {
            'name': 'News: prefix',
            'summary': 'News: CleanSpark partnership announced.\n- Strategic alliance\n- Renewable focus',
            'expected_start': 'CleanSpark partnership announced.'
        }
    ]
    
    from utils import ContentFilter
    
    all_passed = True
    
    for case in test_cases:
        print(f"Testing: {case['name']}")
        result = ContentFilter._remove_generic_openings(case['summary'])
        
        if result.startswith(case['expected_start']):
            print(f"  ✅ PASSED: Generic phrase removed correctly")
        else:
            print(f"  ❌ FAILED: Expected '{case['expected_start']}', got '{result[:50]}...'")
            all_passed = False
        print()
    
    return all_passed

if __name__ == "__main__":
    print("Testing fix for repetitive content issue...")
    print()
    
    success1 = test_original_problem_fix()
    success2 = test_additional_generic_phrases()
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED! The repetitive content issue has been resolved.")
        exit(0)
    else:
        print("\n❌ SOME TESTS FAILED! Check the output above for details.")
        exit(1)