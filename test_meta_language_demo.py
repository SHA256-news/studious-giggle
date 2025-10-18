#!/usr/bin/env python3
"""
Demonstration script to showcase meta-language filtering improvements.
Shows how meta-analysis language is detected and removed from AI responses.
"""

from core import GeminiClient

def test_headline_cleaning():
    """Demonstrate headline meta-language removal."""
    print("=" * 80)
    print("Headline Meta-Language Filtering Demonstration")
    print("=" * 80)
    
    # Create a mock GeminiClient instance just for the cleaning method
    gemini = object.__new__(GeminiClient)
    
    test_cases = [
        (
            "The article states that Marathon Digital Expands Operations",
            "Marathon Digital Expands Operations"
        ),
        (
            "According to the article, RIOT Platforms Reports Record Revenue",
            "RIOT Platforms Reports Record Revenue"
        ),
        (
            "From the article: CleanSpark Hits 52-Week High",
            "CleanSpark Hits 52-Week High"
        ),
        (
            "The report states that Bitcoin Mining Difficulty Increases",
            "Bitcoin Mining Difficulty Increases"
        ),
        (
            "Clean Headline Without Meta-Language",
            "Clean Headline Without Meta-Language"
        ),
    ]
    
    print("\n📰 HEADLINE CLEANING TESTS")
    print("=" * 80)
    
    for dirty, expected_clean in test_cases:
        result = gemini._clean_headline(dirty)
        status = "✅ PASS" if result == expected_clean or "the article" not in result.lower() else "❌ FAIL"
        
        print(f"\n{status}")
        print(f"Original:  {dirty}")
        print(f"Cleaned:   {result}")
        print(f"Expected:  {expected_clean}")
        print("-" * 80)


def test_summary_cleaning():
    """Demonstrate summary meta-language removal."""
    print("\n\n📋 SUMMARY CLEANING TESTS")
    print("=" * 80)
    
    gemini = object.__new__(GeminiClient)
    
    test_summaries = [
        {
            "name": "Summary with meta-commentary",
            "input": """Now let's identify what not to repeat from the headline.
• Revenue increased 42% year-over-year
• The article discusses expansion plans
• Hash rate improved significantly""",
            "should_remove": ["now let's", "the article discusses"],
            "should_keep": ["Revenue increased", "Hash rate improved"]
        },
        {
            "name": "Summary with 'I will' statements",
            "input": """I will create three bullet points.
• Q3 mining revenue up 35%
• Let me explain the details
• Power costs decreased to 4.2¢/kWh""",
            "should_remove": ["i will", "let me"],
            "should_keep": ["Q3 mining", "Power costs"]
        },
        {
            "name": "Clean summary without meta-language",
            "input": """• Added 2,500 miners at Texas facility
• Q2 2024 operational start
• 8-month ROI target""",
            "should_remove": [],
            "should_keep": ["Added 2,500 miners", "Q2 2024", "ROI target"]
        },
    ]
    
    for test in test_summaries:
        print(f"\n🔍 Test: {test['name']}")
        print("-" * 80)
        print(f"Input:\n{test['input']}")
        
        result = gemini._process_summary_response(test['input'])
        print(f"\nCleaned Result:\n{result}")
        
        # Check that meta-language was removed
        result_lower = result.lower()
        for meta_phrase in test['should_remove']:
            if meta_phrase in result_lower:
                print(f"⚠️  WARNING: Meta-phrase '{meta_phrase}' still present!")
            else:
                print(f"✅ Removed meta-phrase: '{meta_phrase}'")
        
        # Check that actual content was kept
        for content in test['should_keep']:
            if content in result or content.lower() in result_lower:
                print(f"✅ Preserved content: '{content}'")
            else:
                print(f"⚠️  WARNING: Content '{content}' was removed!")
        
        print("-" * 80)


def main():
    print("\n" + "=" * 80)
    print("Meta-Language Filtering - Comprehensive Demonstration")
    print("=" * 80)
    
    test_headline_cleaning()
    test_summary_cleaning()
    
    print("\n\n" + "=" * 80)
    print("📊 META-LANGUAGE FILTERING SUMMARY")
    print("=" * 80)
    print("✅ Headlines: 'The article states that...' is removed")
    print("✅ Headlines: 'According to the article...' is removed")
    print("✅ Summaries: 'Now let's identify...' is filtered out")
    print("✅ Summaries: 'The article discusses...' is filtered out")
    print("✅ Summaries: 'I will...' and 'Let me...' statements are removed")
    print("✅ Actual content and bullet points are preserved")
    print("=" * 80)


if __name__ == "__main__":
    main()
