#!/usr/bin/env python3
"""
Demo & Test Runner
-----------------
Consolidated tool for running demonstrations and tests.
Replaces: demo_enhanced_tweets.py, demo_gemini_headlines.py, demo_image_functionality.py, 
         demo_edit_queue.py and various test scripts.
"""

import sys
import argparse
import logging
from typing import Dict, Any, List
from unittest import mock

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class DemoRunner:
    """Consolidated demo and test functionality"""
    
    def demo_enhanced_tweets(self):
        """Demonstrate enhanced tweet formatting (replaces demo_enhanced_tweets.py)"""
        from utils import TextUtils
        
        print("🚀 Enhanced Tweet Formatting Demo")
        print("=" * 80)
        
        # Real-world test cases
        test_cases = [
            {
                "title": "200 BTC Annually: Hong Kong's Investment Holding Company Sets To Bitcoin Mining",
                "body": "DL Holdings, a Hong Kong-based investment holding company, has announced a $21.85 million investment in Bitcoin mining operations through a bond agreement with Fortune Peak.",
                "description": "🏢 Company Investment"
            },
            {
                "title": "CleanSpark Expands Bitcoin Mining Operations with $50 Million Investment",
                "body": "CleanSpark Inc has announced a major expansion of its Bitcoin mining operations with a $50 million investment in a new facility in Texas.",
                "description": "📈 Mining Expansion"
            },
            {
                "title": "SEC Approves First Bitcoin Mining ETF for Institutional Investors",
                "body": "The Securities and Exchange Commission has given approval for the first Bitcoin mining exchange-traded fund.",
                "description": "🏛️ Regulatory Approval"
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n{case['description']} (Test Case {i})")
            print("-" * 60)
            
            # Create mock article
            article = {
                "title": case["title"],
                "body": case["body"],
                "url": f"https://example.com/article{i}",
                "source": {"title": "Bitcoin News"},
                "date": "2024-01-01"
            }
            
            # Show original vs enhanced
            original_tweet = TextUtils.create_original_tweet_text(article)
            enhanced_tweet = TextUtils.create_enhanced_tweet_text(article)
            
            print(f"Original ({len(original_tweet)} chars): {original_tweet}")
            print(f"Enhanced ({len(enhanced_tweet)} chars): {enhanced_tweet}")
            
            # Show improvement
            char_difference = len(enhanced_tweet) - len(original_tweet)
            print(f"📊 Character difference: {char_difference:+d}")
    
    def demo_gemini_headlines(self):
        """Demonstrate Gemini headline generation (replaces demo_gemini_headlines.py)"""
        import os
        
        print("🤖 Gemini AI Headlines Demo")
        print("=" * 60)
        
        if not os.getenv('GEMINI_API_KEY'):
            print("⚠️  GEMINI_API_KEY not set - this demo requires Gemini API access")
            print("   Set the environment variable to test Gemini functionality")
            return
        
        try:
            from gemini_client import GeminiClient
            from config import GeminiConfig
            
            gemini_config = GeminiConfig.from_env()
            gemini_client = GeminiClient(gemini_config)
            
            print("✅ Gemini client initialized successfully")
            
            # Test articles
            test_articles = [
                {
                    "title": "Bitcoin Mining Facility Opens in Texas with 50 MW Capacity",
                    "body": "A new Bitcoin mining facility has opened in Texas with a capacity of 50 megawatts, capable of mining approximately 300 Bitcoin annually.",
                    "description": "🏭 New Facility"
                },
                {
                    "title": "Marathon Digital Holdings Increases Bitcoin Mining Operations",
                    "body": "Marathon Digital Holdings has announced a significant expansion of their Bitcoin mining operations with new hardware deployment.",
                    "description": "🚀 Expansion News"
                }
            ]
            
            for i, article in enumerate(test_articles, 1):
                print(f"\n{article['description']} (Test {i})")
                print("-" * 40)
                print(f"Original: {article['title']}")
                
                try:
                    # Generate Gemini headline
                    gemini_headline = gemini_client.generate_tweet_headline(article)
                    print(f"Gemini:   {gemini_headline}")
                    
                    # Generate summary if available
                    try:
                        gemini_summary = gemini_client.generate_tweet_summary(article)
                        print(f"Summary:  {gemini_summary[:100]}...")
                    except:
                        print("Summary:  [Generation failed]")
                        
                except Exception as e:
                    print(f"Gemini:   [Generation failed: {e}]")
        
        except Exception as e:
            print(f"❌ Gemini client initialization failed: {e}")
    
    def demo_image_functionality(self):
        """Demonstrate image functionality (replaces demo_image_functionality.py)"""
        print("🖼️  Image Functionality Demo")
        print("=" * 60)
        
        try:
            from entity_extractor import EntityExtractor
            from image_library import ImageLibrary
            from image_selector import ImageSelector
            
            print("✅ Image modules imported successfully")
            
            # Initialize components
            extractor = EntityExtractor()
            library = ImageLibrary()
            selector = ImageSelector()
            
            print("✅ Image components initialized")
            
            # Test headlines
            test_headlines = [
                "Michigan Bitcoin Reserve Bill Moves Forward",
                "Texas Bitcoin Mining Farm Expands Operations",
                "SEC Approves New Bitcoin ETF Application"
            ]
            
            for headline in test_headlines:
                print(f"\n📰 Testing: {headline}")
                
                # Entity analysis
                analysis = extractor.analyze_headline(headline)
                print(f"   Entity: {analysis['primary_entity']['type']} - {analysis['primary_entity']['value']}")
                
                # Image selection
                images = selector.select_images_for_headline(headline)
                print(f"   Images: {len(images)} selected")
                
                if images:
                    for img in images[:2]:  # Show first 2
                        print(f"     └─ {img}")
        
        except Exception as e:
            print(f"❌ Image functionality test failed: {e}")
            print("   This is normal if image dependencies are not fully set up")
    
    def run_critical_tests(self):
        """Run critical test scenarios (consolidated from various test files)"""
        print("🧪 Critical Test Scenarios")
        print("=" * 60)
        
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Bot initialization
        tests_total += 1
        try:
            from bot import BitcoinMiningNewsBot
            with mock.patch('bot.APIClientManager'):
                bot = BitcoinMiningNewsBot(safe_mode=True)
            print("✅ Bot initialization test passed")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Bot initialization test failed: {e}")
        
        # Test 2: Config loading
        tests_total += 1
        try:
            from config import BotConstants
            assert hasattr(BotConstants, 'TWEET_MAX_LENGTH')
            assert hasattr(BotConstants, 'MINIMUM_INTERVAL_MINUTES')
            print("✅ Config loading test passed")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Config loading test failed: {e}")
        
        # Test 3: Text utilities
        tests_total += 1
        try:
            from utils import TextUtils
            test_article = {
                "title": "Test Bitcoin Mining Article",
                "url": "https://example.com",
                "body": "Test body content"
            }
            tweet_text = TextUtils.create_enhanced_tweet_text(test_article)
            assert len(tweet_text) > 0
            assert len(tweet_text) <= 280
            print("✅ Text utilities test passed")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Text utilities test failed: {e}")
        
        # Test 4: File management
        tests_total += 1
        try:
            from utils import FileManager
            posted_articles = FileManager.load_posted_articles()
            assert isinstance(posted_articles, dict)
            assert 'posted_uris' in posted_articles
            print("✅ File management test passed")
            tests_passed += 1
        except Exception as e:
            print(f"❌ File management test failed: {e}")
        
        print(f"\n📊 Test Results: {tests_passed}/{tests_total} passed")
        
        if tests_passed == tests_total:
            print("🎉 All critical tests passed!")
        else:
            print("⚠️  Some tests failed - review the errors above")
    
    def run_performance_check(self):
        """Check performance characteristics"""
        import time
        from utils import TextUtils, FileManager
        
        print("⚡ Performance Check")
        print("=" * 40)
        
        # Test article processing speed
        test_article = {
            "title": "Test Bitcoin Mining Performance Article with Long Title to Test Processing Speed",
            "body": "This is a test article body with enough content to test the processing speed of the text utilities and other components.",
            "url": "https://example.com/test",
            "source": {"title": "Test Source"},
            "date": "2024-01-01"
        }
        
        # Time tweet creation
        start_time = time.time()
        for _ in range(100):
            TextUtils.create_enhanced_tweet_text(test_article)
        tweet_time = time.time() - start_time
        
        print(f"✅ Tweet generation: {tweet_time:.3f}s for 100 iterations")
        print(f"   Average: {tweet_time/100*1000:.1f}ms per tweet")
        
        # Time file operations
        start_time = time.time()
        for _ in range(10):
            FileManager.load_posted_articles()
        file_time = time.time() - start_time
        
        print(f"✅ File loading: {file_time:.3f}s for 10 iterations")
        print(f"   Average: {file_time/10*1000:.1f}ms per load")
        
        if tweet_time/100 < 0.01 and file_time/10 < 0.1:
            print("🚀 Performance: Excellent")
        elif tweet_time/100 < 0.05 and file_time/10 < 0.5:
            print("✅ Performance: Good")
        else:
            print("⚠️  Performance: Could be improved")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Bitcoin Mining News Bot Demo & Test Runner")
    parser.add_argument("action", choices=[
        "tweets", "gemini", "images", "tests", "performance", "all"
    ], help="Demo or test to run")
    
    args = parser.parse_args()
    
    runner = DemoRunner()
    
    if args.action == "tweets":
        runner.demo_enhanced_tweets()
    elif args.action == "gemini":
        runner.demo_gemini_headlines()
    elif args.action == "images":
        runner.demo_image_functionality()
    elif args.action == "tests":
        runner.run_critical_tests()
    elif args.action == "performance":
        runner.run_performance_check()
    elif args.action == "all":
        print("🎯 Running All Demos and Tests")
        print("=" * 80)
        
        runner.demo_enhanced_tweets()
        print("\n" + "="*80 + "\n")
        
        runner.demo_gemini_headlines()
        print("\n" + "="*80 + "\n")
        
        runner.demo_image_functionality()
        print("\n" + "="*80 + "\n")
        
        runner.run_critical_tests()
        print("\n" + "="*80 + "\n")
        
        runner.run_performance_check()


if __name__ == "__main__":
    main()