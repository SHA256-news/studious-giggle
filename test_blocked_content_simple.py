#!/usr/bin/env python3
"""
Test blocked content scenarios for runtime logging
"""

import os
import sys
import json
import tempfile

def test_crypto_filtering_scenario():
    """Test crypto filtering logging scenario"""
    print("Testing crypto filtering scenario...")
    
    from runtime_logger import RuntimeLogger
    
    with tempfile.TemporaryDirectory() as temp_dir:
        logger = RuntimeLogger(logs_dir=temp_dir)
        
        # Simulate filtered articles
        ethereum_article = {
            "title": "Ethereum and Bitcoin Mining Comparison",
            "url": "https://example.com/eth-btc",
            "uri": "eth-btc-1",
            "source": {"title": "Crypto News"}
        }
        
        xrp_article = {
            "title": "XRP Mining Platform Launches",
            "url": "https://example.com/xrp",
            "uri": "xrp-1", 
            "source": {"title": "XRP News"}
        }
        
        # Log as crypto filtered
        logger.log_blocked_article(
            ethereum_article,
            "crypto_filter", 
            {"unwanted_cryptos_found": ["ethereum"]}
        )
        
        logger.log_blocked_article(
            xrp_article,
            "crypto_filter",
            {"unwanted_cryptos_found": ["xrp"]}
        )
        
        # Finalize logs
        blocked_count = logger.finalize_logs()
        
        # Verify results
        assert blocked_count == 2, f"Expected 2 blocked articles, got {blocked_count}"
        
        # Check files exist
        blocked_jsonl = os.path.join(temp_dir, "blocked.jsonl")
        blocked_md = os.path.join(temp_dir, "blocked.md")
        
        assert os.path.exists(blocked_jsonl), "blocked.jsonl should exist"
        assert os.path.exists(blocked_md), "blocked.md should exist"
        
        # Verify JSONL content
        with open(blocked_jsonl, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 2
            
            for line in lines:
                entry = json.loads(line.strip())
                assert entry["reason"] == "crypto_filter"
                assert "unwanted_cryptos_found" in entry["details"]
        
        # Verify markdown content
        with open(blocked_md, 'r') as f:
            content = f.read()
            assert "**Total Blocked Articles:** 2" in content
            assert "Crypto Filter (2 articles)" in content
            
        print("✓ Crypto filtering scenario test passed")
        return True

def test_mixed_blocking_scenario():
    """Test mixed blocking scenarios"""
    print("Testing mixed blocking scenarios...")
    
    from runtime_logger import RuntimeLogger
    
    with tempfile.TemporaryDirectory() as temp_dir:
        logger = RuntimeLogger(logs_dir=temp_dir)
        
        # Create various blocked content scenarios
        test_articles = [
            {
                "title": "Dogecoin Mining vs Bitcoin",
                "url": "https://example.com/doge",
                "uri": "doge-1",
                "source": {"title": "Crypto News"}
            },
            {
                "title": "Bitcoin Mining Efficiency Improves", 
                "url": "https://example.com/btc-dup",
                "uri": "btc-duplicate",
                "source": {"title": "Bitcoin News"}
            },
            {
                "title": "New Bitcoin Mining Hardware Released",
                "url": "https://example.com/btc-hw",
                "uri": "btc-hw-1", 
                "source": {"title": "Hardware News"}
            }
        ]
        
        # Log different types of blocking
        logger.log_blocked_article(
            test_articles[0], 
            "crypto_filter",
            {"unwanted_cryptos_found": ["dogecoin"]}
        )
        
        logger.log_duplicate_article(test_articles[1])
        
        logger.log_rate_limited_article(
            test_articles[2],
            {"api_error": "429 Too Many Requests", "reset_time": "2024-01-01T12:00:00Z"}
        )
        
        # Add a failed post
        logger.log_failed_post(
            test_articles[2],
            "Twitter API connection timeout"
        )
        
        # Finalize logs
        blocked_count = logger.finalize_logs()
        
        # Verify results
        assert blocked_count == 4, f"Expected 4 blocked items, got {blocked_count}"
        
        # Check files
        blocked_jsonl = os.path.join(temp_dir, "blocked.jsonl")
        blocked_md = os.path.join(temp_dir, "blocked.md")
        
        assert os.path.exists(blocked_jsonl)
        assert os.path.exists(blocked_md)
        
        # Verify JSONL has all types
        with open(blocked_jsonl, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 4
            
            reasons = [json.loads(line)["reason"] for line in lines]
            assert "crypto_filter" in reasons
            assert "duplicate" in reasons  
            assert "rate_limit" in reasons
            assert "post_failure" in reasons
        
        # Verify markdown summary
        with open(blocked_md, 'r') as f:
            content = f.read()
            assert "**Total Blocked Articles:** 4" in content
            assert "Crypto Filter" in content
            assert "Duplicate" in content
            assert "Rate Limit" in content
            assert "Post Failure" in content
            
        print("✓ Mixed blocking scenarios test passed")
        return True

def test_empty_scenario():
    """Test scenario with no blocked content"""
    print("Testing empty scenario...")
    
    from runtime_logger import RuntimeLogger
    
    with tempfile.TemporaryDirectory() as temp_dir:
        logger = RuntimeLogger(logs_dir=temp_dir)
        
        # Finalize without logging anything
        blocked_count = logger.finalize_logs()
        
        assert blocked_count == 0, f"Expected 0 blocked items, got {blocked_count}"
        
        # Check that files are still created
        blocked_md = os.path.join(temp_dir, "blocked.md")
        assert os.path.exists(blocked_md)
        
        with open(blocked_md, 'r') as f:
            content = f.read()
            assert "No blocked content recorded" in content
            
        # JSONL might not exist if no content was logged
        blocked_jsonl = os.path.join(temp_dir, "blocked.jsonl")
        if os.path.exists(blocked_jsonl):
            with open(blocked_jsonl, 'r') as f:
                lines = f.readlines()
                assert len(lines) == 0
                
        print("✓ Empty scenario test passed")
        return True

def test_github_actions_path():
    """Test that the default GitHub Actions path works"""
    print("Testing GitHub Actions path creation...")
    
    from runtime_logger import RuntimeLogger
    
    # Test with the actual GitHub Actions path
    gh_actions_path = "/home/runner/work/_temp/runtime-logs"
    
    # Create the logger (this should create the directory)
    logger = RuntimeLogger(logs_dir=gh_actions_path)
    
    # Verify directory was created
    assert os.path.exists(gh_actions_path), f"Directory {gh_actions_path} should be created"
    
    # Test logging
    test_article = {
        "title": "Test Article for GitHub Actions",
        "url": "https://example.com/test",
        "uri": "test-gh-1",
        "source": {"title": "Test Source"}
    }
    
    logger.log_blocked_article(test_article, "test_reason", {"test": True})
    blocked_count = logger.finalize_logs()
    
    assert blocked_count == 1
    
    # Verify files exist in the GitHub Actions path
    assert os.path.exists(os.path.join(gh_actions_path, "blocked.jsonl"))
    assert os.path.exists(os.path.join(gh_actions_path, "blocked.md"))
    
    print("✓ GitHub Actions path test passed")
    print(f"  - Created directory: {gh_actions_path}")
    print(f"  - Files ready for artifact upload")
    return True

if __name__ == "__main__":
    try:
        success = True
        success &= test_crypto_filtering_scenario()
        success &= test_mixed_blocking_scenario()
        success &= test_empty_scenario()
        success &= test_github_actions_path()
        
        if success:
            print("\n✅ All blocked content scenario tests passed!")
            print("🎯 Runtime logging system is fully functional")
            print("📦 GitHub Actions will upload artifacts correctly")
            print("🔍 blocked.jsonl and blocked.md files will be available for debugging")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except Exception as e:
        import traceback
        print(f"\n❌ Test failed: {e}")
        traceback.print_exc()
        sys.exit(1)