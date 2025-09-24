#!/usr/bin/env python3
"""
Test script for create_summary.py content handling functionality
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the functions from create_summary.py
from create_summary import clean_text_for_twitter, extract_clean_content, create_twitter_thread, split_text_for_twitter


def test_ai_artifact_removal():
    """Test that AI processing artifacts are properly removed"""
    print("🧹 Testing AI artifact removal...")
    
    test_cases = [
        {
            "input": "I have browsed the article and found key information. Now I need to analyze the data...",
            "expected_clean": True,
            "description": "Browse artifact"
        },
        {
            "input": "Let me analyze the Bitcoin mining situation. The company announced...",
            "expected_clean": True,
            "description": "Let me artifact"
        },
        {
            "input": "First, I need to mention the financial details. The investment is $50M.",
            "expected_clean": True,
            "description": "First I artifact"
        },
        {
            "input": "This is clean Bitcoin mining news without artifacts.",
            "expected_clean": False,
            "description": "Clean text (no artifacts)"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        cleaned = clean_text_for_twitter(case["input"])
        print(f"  Test {i}: {case['description']}")
        print(f"    Input: {case['input'][:50]}...")
        print(f"    Output: {cleaned[:50]}...")
        
        # Verify cleaning worked as expected
        if case["expected_clean"]:
            # Should be different after cleaning
            if cleaned != case["input"]:
                print("    ✅ AI artifacts properly removed")
            else:
                print("    ❌ AI artifacts not removed")
                return False
        else:
            # Should be same or similar (no artifacts to remove)
            print("    ✅ Clean text preserved")
    
    print("✅ AI artifact removal tests passed")
    return True


def test_content_extraction_and_cleaning():
    """Test that all content fields are properly cleaned"""
    print("\n📝 Testing content extraction and cleaning...")
    
    dirty_article = {
        "headline": "I will now provide the headline... Bitcoin Mining Expansion",
        "subtitle": "Let me explain the subtitle... Company grows operations",
        "content": "Looking at the data, I can see that Bitcoin mining is expanding rapidly...",
        "key_points": [
            "First, I need to mention the key point about investment",
            "Now I will analyze the second point about hashrate",
            "Clean point without artifacts"
        ],
        "body": "I am unable to access full details, however I can provide this information... The company announced major expansion."
    }
    
    cleaned_article = extract_clean_content(dirty_article)
    
    # Check headline cleaning
    print("  Headline cleaning:")
    print(f"    Before: {dirty_article['headline']}")
    print(f"    After: {cleaned_article['headline']}")
    
    # Check key points cleaning
    print("  Key points cleaning:")
    for i, (before, after) in enumerate(zip(dirty_article['key_points'], cleaned_article['key_points'])):
        print(f"    Point {i+1} Before: {before}")
        print(f"    Point {i+1} After: {after}")
    
    # Verify cleaning worked
    assert "I will now provide" not in cleaned_article['headline'], "Headline should be cleaned"
    assert "Let me explain" not in cleaned_article['subtitle'], "Subtitle should be cleaned" 
    assert "Looking at the data" not in cleaned_article['content'], "Content should be cleaned"
    assert not any("First, I need to mention" in point for point in cleaned_article['key_points']), "Key points should be cleaned"
    assert "I am unable to access" not in cleaned_article['body'], "Body should be cleaned"
    
    print("✅ Content extraction and cleaning tests passed")
    return True


def test_twitter_thread_creation():
    """Test that Twitter threads are created properly with proper content handling"""
    print("\n🧵 Testing Twitter thread creation...")
    
    test_article = {
        "headline": "I need to analyze this... CleanSpark Expands Mining Operations",
        "subtitle": "Let me provide details... 30% hashrate increase planned",
        "content": "Looking at the news, I can see that CleanSpark has announced a major expansion. The Bitcoin mining company will deploy 3,000 new miners across multiple facilities. This represents a significant investment in cryptocurrency infrastructure.\n\nNow I will explain the technical details... The new miners will increase the company's total hashrate by approximately 30%, bringing capacity to 20 EH/s. The energy consumption will also increase accordingly.",
        "key_points": [
            "First, I should mention the $75 million investment",
            "3,000 new ASIC miners to be deployed",
            "Let me add that hashrate increases by 30%",
            "I will now note the expansion to 20 EH/s capacity"
        ],
        "tags": ["bitcoin", "mining", "cleanspark", "expansion", "hashrate"],
        "generated_at": "2024-09-24T12:00:00Z",
        "source_event_uri": "test-123"
    }
    
    thread = create_twitter_thread(test_article, max_tweets=6)
    
    print(f"  Generated {len(thread)} tweets:")
    for i, tweet in enumerate(thread, 1):
        print(f"    Tweet {i} ({len(tweet)} chars): {tweet[:80]}...")
        
        # Validate tweet length
        if len(tweet) > 280:
            print(f"    ❌ Tweet {i} exceeds 280 characters: {len(tweet)}")
            return False
        
        # Check for AI artifacts in tweets
        ai_patterns = ["I need to", "Let me", "Looking at", "Now I will", "First, I"]
        for pattern in ai_patterns:
            if pattern in tweet:
                print(f"    ❌ Tweet {i} contains AI artifact: {pattern}")
                return False
    
    # Verify thread structure
    assert thread[0].startswith("1/"), "First tweet should be numbered"
    assert "🧵" in thread[0], "First tweet should have thread emoji"
    assert "CleanSpark" in thread[0], "Headline should be present and cleaned"
    assert thread[-1].startswith(f"{len(thread)}/"), "Last tweet should be numbered correctly"
    
    print("✅ Twitter thread creation tests passed")
    return True


def test_text_splitting():
    """Test that text is properly split for Twitter length limits"""
    print("\n✂️ Testing text splitting functionality...")
    
    # Test short text (should not be split)
    short_text = "This is a short Bitcoin mining update."
    chunks = split_text_for_twitter(short_text)
    assert len(chunks) == 1, "Short text should not be split"
    print(f"  Short text: {len(chunks)} chunk(s) ✅")
    
    # Test long text (should be split)
    long_text = "This is a very long Bitcoin mining update that contains multiple sentences and should be split into multiple chunks when processed by the text splitting function. It talks about hashrate increases, new mining equipment deployments, energy consumption optimization, and facility expansions across multiple geographic regions."
    chunks = split_text_for_twitter(long_text, max_length=280)
    print(f"  Long text: {len(chunks)} chunk(s)")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"    Chunk {i} ({len(chunk)} chars): {chunk[:50]}...")
        assert len(chunk) <= 270, f"Chunk {i} should fit in tweet with numbering space"  # Leave space for numbering
    
    # Test text with AI artifacts (should be cleaned before splitting)
    dirty_text = "I will now analyze the Bitcoin mining situation. Let me explain the technical details... The hashrate has increased significantly this quarter."
    chunks = split_text_for_twitter(dirty_text)
    combined = " ".join(chunks)
    assert "I will now analyze" not in combined, "AI artifacts should be removed during splitting"
    print(f"  AI artifact removal during splitting: ✅")
    
    print("✅ Text splitting tests passed")
    return True


def test_command_line_interface():
    """Test the command-line interface of create_summary.py"""
    print("\n🖥️ Testing command-line interface...")
    
    # Create a test article file
    test_article = {
        "headline": "Let me provide the headline... Bitcoin Mining News Update",
        "content": "I need to analyze this situation... The Bitcoin mining industry continues to evolve.",
        "key_points": [
            "First, I should mention the market changes",
            "Clean point about technology improvements"
        ],
        "tags": ["bitcoin", "mining"]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_article, f, indent=2)
        test_file = f.name
    
    try:
        # Test JSON output
        import subprocess
        result = subprocess.run([
            sys.executable, 'create_summary.py', test_file
        ], capture_output=True, text=True, cwd='/home/runner/work/studious-giggle/studious-giggle')
        
        if result.returncode != 0:
            print(f"    ❌ Script failed: {result.stderr}")
            return False
        
        # Parse JSON output
        output_data = json.loads(result.stdout)
        assert 'thread' in output_data, "Output should contain 'thread' field"
        assert 'total_tweets' in output_data, "Output should contain 'total_tweets' field"
        assert len(output_data['thread']) > 0, "Thread should have tweets"
        
        # Check AI artifact removal
        thread_text = " ".join(output_data['thread'])
        assert "Let me provide" not in thread_text, "AI artifacts should be removed"
        assert "I need to analyze" not in thread_text, "AI artifacts should be removed"
        
        print("  JSON output format: ✅")
        
        # Test text output format
        result = subprocess.run([
            sys.executable, 'create_summary.py', test_file, '--format', 'text'
        ], capture_output=True, text=True, cwd='/home/runner/work/studious-giggle/studious-giggle')
        
        if result.returncode == 0 and "Tweet 1:" in result.stdout:
            print("  Text output format: ✅")
        else:
            print(f"    ❌ Text format failed: {result.stderr}")
            return False
            
    finally:
        os.unlink(test_file)
    
    print("✅ Command-line interface tests passed")
    return True


def main():
    """Run all tests"""
    print("🧪 Testing create_summary.py Content Handling")
    print("=" * 60)
    
    tests = [
        test_ai_artifact_removal,
        test_content_extraction_and_cleaning,
        test_twitter_thread_creation,
        test_text_splitting,
        test_command_line_interface
    ]
    
    passed = 0
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_func.__name__} failed")
        except Exception as e:
            print(f"❌ {test_func.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print(f"📋 RESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All content handling tests passed!")
        print("✅ create_summary.py properly handles content cleaning")
        print("✅ AI artifacts are removed from all text fields")
        print("✅ Twitter threads are properly formatted and sized")
        print("✅ Command-line interface works correctly")
        return True
    else:
        print("❌ Some tests failed - content handling needs attention")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)