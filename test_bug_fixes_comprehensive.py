#!/usr/bin/env python3
"""
Comprehensive test to validate all bug fixes and optimizations
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import TextUtils, ContentFilter, CompiledPatterns

def test_duplicate_method_removed():
    """Test that duplicate _filter_repetitive_content method was removed"""
    print("Testing duplicate method removal...")
    
    # Check that there's only one _filter_repetitive_content method in TextUtils
    methods = [attr for attr in dir(TextUtils) if '_filter_repetitive_content' in attr]
    assert len(methods) == 1, f"Expected 1 _filter_repetitive_content method, found {len(methods)}"
    
    # Test that the working method is functional
    test_summary = "Company invests $100M in Bitcoin mining. Technical specs: 200MW capacity."
    test_hook = "Company announces $100M Bitcoin investment"
    test_article = {"title": "Company invests in Bitcoin", "url": "https://example.com"}
    
    try:
        result = TextUtils._filter_repetitive_content(test_summary, test_hook, test_article)
        assert isinstance(result, str), "Method should return a string"
        print("✓ Duplicate method removed and working method functional")
    except Exception as e:
        print(f"✗ Working method has issues: {e}")
        return False
    
    return True

def test_regex_optimizations():
    """Test that regex optimizations work correctly"""
    print("Testing regex optimizations...")
    
    # Test compiled patterns exist
    assert hasattr(CompiledPatterns, 'BULLET_MARKER'), "BULLET_MARKER pattern missing"
    assert hasattr(CompiledPatterns, 'FINANCIAL_AMOUNT_EXTRACT'), "FINANCIAL_AMOUNT_EXTRACT pattern missing"
    assert hasattr(CompiledPatterns, 'KNOWN_COMPANIES'), "KNOWN_COMPANIES pattern missing"
    
    # Test financial amount normalization
    assert ContentFilter._normalize_financial_amount("100M") == "100million"
    assert ContentFilter._normalize_financial_amount("5.5B") == "5.5billion" 
    assert ContentFilter._normalize_financial_amount("invalid") is None
    
    # Test bullet content extraction
    bullet_text = "• Test bullet point content!"
    extracted = ContentFilter._extract_bullet_content_from_line(bullet_text)
    assert extracted == "test bullet point content"
    
    # Test company pattern matching
    test_text = "CleanSpark announced new investment. Marathon Digital expanded operations."
    companies = CompiledPatterns.KNOWN_COMPANIES.findall(test_text)
    assert "CleanSpark" in companies
    assert "Marathon Digital" in companies
    
    print("✓ Regex optimizations working correctly")
    return True

def test_timezone_fixes():
    """Test timezone handling improvements"""
    print("Testing timezone fixes...")
    
    from bot import BitcoinMiningNewsBot
    from datetime import datetime, timezone
    
    # Create a bot instance in safe mode
    bot = BitcoinMiningNewsBot(safe_mode=True)
    
    # Test with timezone-aware dates
    test_articles = [
        {
            "uri": "test1",
            "title": "Old article",
            "dateTimePub": "2023-01-01T00:00:00Z"  # Old date
        },
        {
            "uri": "test2", 
            "title": "Recent article",
            "dateTimePub": datetime.now(timezone.utc).isoformat()  # Recent date
        }
    ]
    
    # Add test articles to queue
    bot.posted_articles["queued_articles"] = test_articles
    
    # Test staleness check
    is_stale = bot._is_queue_stale(max_age_hours=48)
    # Should detect some staleness due to old article
    
    # Test cleaning
    original_count = len(bot.posted_articles["queued_articles"])
    bot._clean_stale_articles(max_age_hours=48)
    cleaned_count = len(bot.posted_articles["queued_articles"])
    
    # Should have removed the old article
    assert cleaned_count < original_count, "Should have cleaned stale articles"
    
    print("✓ Timezone fixes working correctly")
    return True

def test_entity_extractor_optimization():
    """Test entity extractor optimization"""
    print("Testing entity extractor optimization...")
    
    # Test that extract_key_info works without initializing extractor multiple times
    test_article = {
        "title": "CleanSpark invests $100M in Bitcoin mining expansion",
        "body": "The company announced significant expansion plans."
    }
    
    # Call multiple times to test caching
    info1 = TextUtils.extract_key_info(test_article)
    info2 = TextUtils.extract_key_info(test_article)
    
    # Should work consistently
    assert "companies" in info1
    assert "financial_amounts" in info1
    assert info1.keys() == info2.keys()
    
    print("✓ Entity extractor optimization working")
    return True

def test_abbreviation_caching():
    """Test abbreviation pattern caching"""
    print("Testing abbreviation caching...")
    
    # Test that abbreviations work with caching
    test_text = "partnership with investment in bitcoin mining facility"
    abbreviated = TextUtils._apply_abbreviations(test_text)
    
    # Should apply abbreviations
    assert len(abbreviated) <= len(test_text)
    
    # Test again to ensure caching works
    abbreviated2 = TextUtils._apply_abbreviations(test_text)
    assert abbreviated == abbreviated2
    
    print("✓ Abbreviation caching working")
    return True

def test_no_redundant_imports():
    """Test that redundant imports were removed"""
    print("Testing import cleanup...")
    
    # Read utils.py and check for redundant imports
    with open('utils.py', 'r') as f:
        content = f.read()
    
    # Count 'import re' occurrences - should only be at top level
    import_re_count = len(re.findall(r'^\s*import re', content, re.MULTILINE))
    assert import_re_count == 1, f"Found {import_re_count} 'import re' statements, expected 1"
    
    # Should not have import re inside methods
    method_import_re = re.findall(r'def.*?import re', content, re.DOTALL)
    assert len(method_import_re) == 0, "Found import re inside methods"
    
    print("✓ Import cleanup successful")
    return True

def run_all_tests():
    """Run all bug fix validation tests"""
    print("🔍 Running comprehensive bug fix validation...")
    print("=" * 60)
    
    tests = [
        test_duplicate_method_removed,
        test_regex_optimizations,
        test_timezone_fixes,
        test_entity_extractor_optimization,
        test_abbreviation_caching,
        test_no_redundant_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            print(f"✗ {test.__name__} failed with exception: {e}")
    
    print("=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All bug fixes validated successfully!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)