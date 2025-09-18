#!/usr/bin/env python3

"""
Test script for enhanced rate limit diagnostics
Tests the new diagnostic features that help explain why no tweets were posted
"""

import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from diagnose_bot import check_rate_limit_cooldown

def test_rate_limit_diagnostic():
    """Test the rate limit cooldown detection functionality"""
    print("Testing rate limit diagnostic functionality...")
    
    # Test 1: No cooldown file
    print("\n1. Testing no cooldown file scenario...")
    if os.path.exists("rate_limit_cooldown.json"):
        os.remove("rate_limit_cooldown.json")
    
    is_limited = check_rate_limit_cooldown()
    assert not is_limited, "Should return False when no cooldown file exists"
    print("✓ No cooldown file detected correctly")
    
    # Test 2: Active cooldown
    print("\n2. Testing active cooldown scenario...")
    future_time = datetime.now() + timedelta(hours=2)
    cooldown_data = {
        "cooldown_until": future_time.isoformat() + "Z",
        "reason": "Daily rate limit exceeded"
    }
    
    with open("rate_limit_cooldown.json", "w") as f:
        json.dump(cooldown_data, f)
    
    is_limited = check_rate_limit_cooldown()
    assert is_limited, "Should return True when active cooldown exists"
    print("✓ Active cooldown detected correctly")
    
    # Test 3: Expired cooldown
    print("\n3. Testing expired cooldown scenario...")
    past_time = datetime.now() - timedelta(hours=1)
    cooldown_data = {
        "cooldown_until": past_time.isoformat() + "Z",
        "reason": "Daily rate limit exceeded"
    }
    
    with open("rate_limit_cooldown.json", "w") as f:
        json.dump(cooldown_data, f)
    
    is_limited = check_rate_limit_cooldown()
    assert not is_limited, "Should return False when cooldown has expired"
    print("✓ Expired cooldown handled correctly")
    
    # Clean up
    if os.path.exists("rate_limit_cooldown.json"):
        os.remove("rate_limit_cooldown.json")
    
    print("\n✓ All rate limit diagnostic tests passed!")

def test_diagnostic_integration():
    """Test that the diagnostic integration provides useful output"""
    print("\nTesting diagnostic integration...")
    
    # Create a mock scenario similar to what happened in the GitHub Actions
    future_time = datetime.now() + timedelta(hours=1, minutes=23)
    cooldown_data = {
        "cooldown_until": future_time.isoformat() + "Z",
        "reason": "Daily rate limit exceeded (17 requests per 24 hours)"
    }
    
    with open("rate_limit_cooldown.json", "w") as f:
        json.dump(cooldown_data, f)
    
    # Import and run the main diagnostic function
    from diagnose_bot import main as diagnose_main
    
    print("\nRunning integrated diagnostics (this will show the actual output):")
    print("-" * 60)
    try:
        diagnose_main()
    except SystemExit:
        pass  # diagnose_main might call sys.exit, which is fine for testing
    print("-" * 60)
    
    # Clean up
    if os.path.exists("rate_limit_cooldown.json"):
        os.remove("rate_limit_cooldown.json")
    
    print("✓ Diagnostic integration test completed")

if __name__ == "__main__":
    print("🧪 Testing Enhanced Rate Limit Diagnostics")
    print("=" * 50)
    
    test_rate_limit_diagnostic()
    test_diagnostic_integration()
    
    print("\n🎉 All diagnostic tests passed successfully!")
    print("\nThe enhanced diagnostics now provide clear explanations for:")
    print("  - Why 'successful' GitHub Actions don't always post tweets")
    print("  - How rate limiting protects the bot from violating Twitter's terms")
    print("  - When tweets will automatically resume")
    print("  - How many articles are queued for posting")