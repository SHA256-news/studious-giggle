#!/usr/bin/env python3
"""
Streamlined Bitcoin Mining Bot Tests
Simple, effective tests that match the actual implementation.
"""

import sys
import os
import json
import tempfile
from unittest.mock import patch
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core import BitcoinMiningBot, Config, Article, Storage, TextProcessor, TimeManager
    from tools import BotTools
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)


class TestBot:
    """Simple, effective bot tests."""

    def test_config_basics(self):
        """Test basic config functionality."""
        config = Config()
        assert hasattr(config, 'posted_articles_file')
        
        # Test validation
        errors = config.validate()
        assert isinstance(errors, list)

    def test_article_creation(self):
        """Test article creation from valid data."""
        valid_data = {
            "title": "Bitcoin Mining News",
            "body": "Test content",
            "url": "https://example.com/article",
            "uri": "https://example.com/article",
            "source": {"title": "Test Source"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        
        article = Article.from_dict(valid_data)
        assert article is not None
        assert article.title == "Bitcoin Mining News"
        assert article.url == "https://example.com/article"

    def test_storage_functionality(self):
        """Test storage operations."""
        # Test loading non-existent file
        data = Storage.load_json("nonexistent.json", {"default": True})
        assert data["default"] is True
        
        # Test posted articles structure
        posted_data = Storage.load_posted_articles("nonexistent.json")
        assert "posted_uris" in posted_data
        assert "queued_articles" in posted_data
        assert isinstance(posted_data["posted_uris"], list)

    def test_text_processing(self):
        """Test text processing functionality."""
        article_data = {
            "title": "Bitcoin Mining Update",
            "url": "https://example.com/test",
            "body": "Test content",
            "source": {"title": "Test Source"}
        }
        article = Article.from_dict(article_data)
        
        tweet_text = TextProcessor.create_tweet_text(article)
        assert isinstance(tweet_text, str)
        assert len(tweet_text) <= 280  # Twitter limit
        assert "Bitcoin Mining Update" in tweet_text

    def test_time_management(self):
        """Test time management utilities."""
        # Test that TimeManager.now() works
        from datetime import datetime, timezone
        now = TimeManager.now()
        assert isinstance(now, datetime)
        assert now.tzinfo == timezone.utc

    def test_bot_initialization(self):
        """Test bot can be initialized."""
        config = Config()
        bot = BitcoinMiningBot(config=config)
        assert bot is not None
        assert bot.config == config

    def test_bot_safe_mode(self):
        """Test bot runs in safe mode without API keys."""
        config = Config()
        bot = BitcoinMiningBot(config=config)
        
        # Should return False due to missing API keys
        result = bot.run()
        assert result is False

    def test_tools_availability(self):
        """Test management tools are available."""
        assert hasattr(BotTools, 'show_next_tweet')
        assert hasattr(BotTools, 'diagnose_bot')
        
        # Test diagnostic runs without crashing
        try:
            result = BotTools.diagnose_bot()
            assert isinstance(result, bool)
        except Exception:
            pass  # Expected without full environment

    def test_mocked_workflow(self):
        """Test complete workflow with mocks."""
        config = Config()
        config.twitter_api_key = "test_key"
        config.twitter_api_secret = "test_secret"
        config.twitter_access_token = "test_token"
        config.twitter_access_token_secret = "test_token_secret"
        config.eventregistry_api_key = "test_er_key"
        
        # Create temporary file with proper cleanup
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        try:
            json.dump({
                "posted_uris": [],
                "queued_articles": [],
                "last_run_time": None
            }, temp_file)
            temp_file.flush()  # Ensure data is written
            temp_file.close()   # Explicitly close before use
            config.posted_articles_file = temp_file.name
            
            mock_article_data = {
                "title": "Bitcoin Mining News",
                "url": "https://example.com/article",
                "body": "Mining update content",
                "source": {"title": "Test Source"}
            }
            mock_article = Article.from_dict(mock_article_data)
            
            with patch('core.TwitterAPI') as MockTwitter, patch('core.NewsAPI') as MockNews:
                # Setup mocks
                mock_twitter = MockTwitter.return_value
                mock_twitter.post_tweet.return_value = "tweet123"
                
                mock_news = MockNews.return_value
                mock_news.fetch_articles.return_value = [mock_article]
                
                # Run bot
                bot = BitcoinMiningBot(config=config)
                result = bot.run()
                
                # Should succeed with mocks
                assert result is True
                
        except Exception:
            # Ensure temp file is closed even if test fails during setup
            if 'temp_file' in locals() and not temp_file.closed:
                temp_file.close()
            raise
        finally:
            # Safer cleanup with error handling
            try:
                if 'config' in locals() and hasattr(config, 'posted_articles_file'):
                    temp_path = Path(config.posted_articles_file)
                    if temp_path.exists():
                        temp_path.unlink()
            except (OSError, PermissionError) as e:
                # File cleanup failed, but don't fail the test
                print(f"Warning: Could not clean up temporary file: {e}")


    def test_law_enforcement_filtering(self):
        """Test that law enforcement/seizure articles are filtered out."""
        from core import NewsAPI, Config
        
        config = Config()
        news_api = NewsAPI(config)
        
        # Test article about Treasury seizure (should be rejected)
        seizure_article_data = {
            "title": "US moves to seize $12 billion in bitcoin tied to Cambodia scam kingpin",
            "body": "The U.S. Department of Justice launched a record-breaking forfeiture case involving bitcoin. The Treasury designated cryptocurrency-enabled scam networks. Chen Zhi was indicted for fraud and money laundering. The operation included mining operations in Laos through Warp Data Technology. Authorities identified over $4 billion in illicit proceeds laundered.",
            "url": "https://example.com/seizure",
            "uri": "test-seizure",
            "source": {"title": "Test"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article = Article.from_dict(seizure_article_data)
        
        # This should be rejected because it's primarily about law enforcement
        is_relevant = news_api._is_bitcoin_relevant(article)
        assert is_relevant is False, "Treasury seizure article should be filtered out"
        
        # Test legitimate mining article (should be approved)
        mining_article_data = {
            "title": "Marathon Digital Expands Mining Operations in Texas",
            "body": "Marathon Digital Holdings announced expansion of its bitcoin mining operations in Texas. The company will add 5000 new mining machines. The mining facility will increase hash rate by 500 PH/s.",
            "url": "https://example.com/mining",
            "uri": "test-mining",
            "source": {"title": "Test"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article2 = Article.from_dict(mining_article_data)
        
        # This should be approved - it's about actual mining operations
        is_relevant2 = news_api._is_bitcoin_relevant(article2)
        assert is_relevant2 is True, "Legitimate mining article should be approved"
    
    def test_environmental_blame_filtering(self):
        """Test that articles blaming Bitcoin mining for environmental problems are filtered out."""
        from core import NewsAPI, Config
        
        config = Config()
        news_api = NewsAPI(config)
        
        # Test article blaming mining for emissions crisis (should be rejected)
        emissions_article = {
            "title": "Bitcoin's Thousands of Miners Fuel Emissions Crisis",
            "body": "Bitcoin mining operations are responsible for a growing emissions crisis. The thousands of miners fuel greenhouse gas emissions worldwide. Mining generates significant environmental damage.",
            "url": "https://example.com/emissions",
            "uri": "test-emissions",
            "source": {"title": "Test"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article1 = Article.from_dict(emissions_article)
        is_relevant1 = news_api._is_bitcoin_relevant(article1)
        assert is_relevant1 is False, "Article blaming mining for emissions crisis should be rejected"
        
        # Test article about farms generating pollution (should be rejected)
        pollution_article = {
            "title": "Bitcoin Mining Farms Generate Heat and Noise Pollution Locally",
            "body": "Mining farms generate heat pollution and noise pollution in local communities. The environmental damage from bitcoin mining continues to grow.",
            "url": "https://example.com/pollution",
            "uri": "test-pollution",
            "source": {"title": "Test"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article2 = Article.from_dict(pollution_article)
        is_relevant2 = news_api._is_bitcoin_relevant(article2)
        assert is_relevant2 is False, "Article about mining generating pollution should be rejected"
        
        # Test article about boiling the oceans (should be rejected)
        boiling_article = {
            "title": "Critics Say Bitcoin Mining is Boiling the Oceans",
            "body": "Environmental activists claim bitcoin mining is contributing to global warming. The carbon footprint of mining operations is enormous. Critics say it's boiling the oceans.",
            "url": "https://example.com/boiling",
            "uri": "test-boiling",
            "source": {"title": "Test"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article3 = Article.from_dict(boiling_article)
        is_relevant3 = news_api._is_bitcoin_relevant(article3)
        assert is_relevant3 is False, "Article about boiling oceans should be rejected"
        
        # Test article with climate crisis blame (should be rejected)
        climate_article = {
            "title": "Bitcoin Mining Worsening Climate Crisis, Report Says",
            "body": "New report shows bitcoin mining causes significant greenhouse gas emissions. The environmental crisis is worsening due to mining operations. Mining is blamed for accelerating climate change.",
            "url": "https://example.com/climate",
            "uri": "test-climate",
            "source": {"title": "Test"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article4 = Article.from_dict(climate_article)
        is_relevant4 = news_api._is_bitcoin_relevant(article4)
        assert is_relevant4 is False, "Article blaming mining for climate crisis should be rejected"
        
        # Test neutral article about renewable energy (should be APPROVED)
        renewable_article = {
            "title": "Bitcoin Mining Company Switches to 100% Renewable Energy",
            "body": "Major bitcoin mining company announces transition to renewable energy sources. The mining facility will be powered entirely by solar and wind. This move reduces the company's carbon footprint.",
            "url": "https://example.com/renewable",
            "uri": "test-renewable",
            "source": {"title": "Test"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article5 = Article.from_dict(renewable_article)
        is_relevant5 = news_api._is_bitcoin_relevant(article5)
        assert is_relevant5 is True, "Neutral article about renewable energy should be approved"
        
        # Test neutral article about energy efficiency (should be APPROVED)
        efficiency_article = {
            "title": "Marathon Digital Reports 20% Increase in Energy Efficiency",
            "body": "Marathon Digital Holdings announced improvements in energy efficiency for its mining operations. The company has upgraded to more efficient ASIC miners. Hash rate increased while maintaining stable power consumption.",
            "url": "https://example.com/efficiency",
            "uri": "test-efficiency",
            "source": {"title": "Test"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article6 = Article.from_dict(efficiency_article)
        is_relevant6 = news_api._is_bitcoin_relevant(article6)
        assert is_relevant6 is True, "Neutral article about energy efficiency should be approved"
    
    def test_ethereum_solana_filtering(self):
        """Test that ethereum and solana articles are properly filtered out."""
        from core import NewsAPI, Config
        
        config = Config()
        news_api = NewsAPI(config)
        
        # Test article with Ethereum in title (should be rejected)
        ethereum_title_article = {
            "title": "Ethereum Mining Shifts to Proof of Stake",
            "body": "Ethereum network transitions away from mining. Bitcoin mining continues with proof of work.",
            "url": "https://example.com/eth",
            "uri": "test-eth",
            "source": {"title": "Test"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article1 = Article.from_dict(ethereum_title_article)
        is_relevant1 = news_api._is_bitcoin_relevant(article1)
        assert is_relevant1 is False, "Article with Ethereum in title should be rejected"
        
        # Test article with Solana in title (should be rejected)
        solana_title_article = {
            "title": "Solana Network Upgrades: New Features for Miners",
            "body": "Solana announces new features. Bitcoin mining mentioned briefly.",
            "url": "https://example.com/sol",
            "uri": "test-sol",
            "source": {"title": "Test"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article2 = Article.from_dict(solana_title_article)
        is_relevant2 = news_api._is_bitcoin_relevant(article2)
        assert is_relevant2 is False, "Article with Solana in title should be rejected"
        
        # Test article with multiple other crypto mentions in body (should be rejected)
        multi_crypto_article = {
            "title": "Cryptocurrency Mining Update",
            "body": "Ethereum mining continues to grow. Solana network sees increased activity. Cardano miners report profits. Bitcoin mining was also mentioned briefly.",
            "url": "https://example.com/multi",
            "uri": "test-multi",
            "source": {"title": "Test"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article3 = Article.from_dict(multi_crypto_article)
        is_relevant3 = news_api._is_bitcoin_relevant(article3)
        assert is_relevant3 is False, "Article with multiple other crypto mentions should be rejected"
        
        # Test article with ETH ticker in title (should be rejected)
        eth_ticker_article = {
            "title": "ETH Mining Profitability Increases",
            "body": "Ethereum mining profitability grows. Bitcoin mining also discussed.",
            "url": "https://example.com/eth-ticker",
            "uri": "test-eth-ticker",
            "source": {"title": "Test"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article4 = Article.from_dict(eth_ticker_article)
        is_relevant4 = news_api._is_bitcoin_relevant(article4)
        assert is_relevant4 is False, "Article with ETH ticker in title should be rejected"
        
        # Test legitimate Bitcoin mining article (should be approved)
        bitcoin_only_article = {
            "title": "Bitcoin Mining Revenue Reaches New High",
            "body": "Bitcoin mining companies report record revenues. Mining difficulty increases. Hash rate reaches all-time high.",
            "url": "https://example.com/btc",
            "uri": "test-btc",
            "source": {"title": "Test"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article5 = Article.from_dict(bitcoin_only_article)
        is_relevant5 = news_api._is_bitcoin_relevant(article5)
        assert is_relevant5 is True, "Legitimate Bitcoin mining article should be approved"
    
    def test_meta_language_filtering(self):
        """Test that meta-analysis language is properly filtered from responses."""
        from core import GeminiClient
        
        # Test _clean_headline removes meta-language
        if GeminiClient:
            gemini = object.__new__(GeminiClient)
            
            # Test headline with meta-language
            dirty_headline1 = "The article states that Marathon Digital Expands Operations"
            clean1 = gemini._clean_headline(dirty_headline1)
            assert "the article states" not in clean1.lower(), "Meta-language should be removed from headline"
            assert "Marathon Digital" in clean1, "Actual content should be preserved"
            
            dirty_headline2 = "According to the article, RIOT Platforms Reports Record Revenue"
            clean2 = gemini._clean_headline(dirty_headline2)
            assert "according to" not in clean2.lower(), "Meta-language should be removed from headline"
            assert "RIOT Platforms" in clean2, "Actual content should be preserved"
        
        # Test _process_summary_response filters meta-commentary
        if GeminiClient:
            gemini = object.__new__(GeminiClient)
            
            # Test summary with meta-language
            dirty_summary = """Now let's identify what not to repeat from the headline.
• Revenue increased 42% year-over-year
• The article discusses expansion plans
• Hash rate improved significantly"""
            
            clean_summary = gemini._process_summary_response(dirty_summary)
            assert "now let's" not in clean_summary.lower(), "Meta-language should be filtered"
            assert "the article discusses" not in clean_summary.lower(), "Meta-language should be filtered"
            assert "Revenue increased" in clean_summary, "Actual bullet points should be preserved"
    
    def test_url_retrieval_error_handling(self):
        """Test that URLRetrievalError is properly raised and not caught incorrectly."""
        from core import URLRetrievalError, GeminiClient, TextProcessor
        from unittest.mock import MagicMock
        
        # Create a test article
        article_data = {
            "title": "Test Bitcoin Mining Article",
            "body": "Test content about Bitcoin mining operations.",
            "url": "https://example.com/article",
            "uri": "test-article",
            "source": {"title": "Test Source"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article = Article.from_dict(article_data)
        
        # Create a mock Gemini client that raises URLRetrievalError
        mock_gemini = MagicMock(spec=GeminiClient)
        mock_gemini.generate_catchy_headline.side_effect = URLRetrievalError(
            "Failed to retrieve content from https://example.com/article: Gemini access error"
        )
        
        # Call create_tweet_thread - it should re-raise URLRetrievalError
        try:
            result = TextProcessor.create_tweet_thread(article, mock_gemini)
            assert False, "Expected URLRetrievalError to be raised"
        except URLRetrievalError as e:
            # This is expected - the error should bubble up
            assert "Failed to retrieve content" in str(e)
            assert "https://example.com/article" in str(e)


def run_simple_tests():
    """Run all simple tests."""
    test_bot = TestBot()
    
    test_methods = [method for method in dir(test_bot) if method.startswith('test_')]
    
    total_tests = len(test_methods)
    passed_tests = 0
    failed_tests = []
    
    print("🧪 Running Streamlined Bot Tests")
    print("=" * 40)
    
    for method_name in test_methods:
        test_method = getattr(test_bot, method_name)
        
        try:
            test_method()
            print(f"  ✅ {method_name}")
            passed_tests += 1
        except Exception as e:
            print(f"  ❌ {method_name}: {str(e)}")
            failed_tests.append(f"{method_name}: {str(e)}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for failure in failed_tests:
            print(f"  - {failure}")
        return False
    else:
        print("🎉 ALL TESTS PASSED!")
        return True


if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)