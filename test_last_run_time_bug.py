#!/usr/bin/env python3
"""
Test script to verify the last_run_time bug in utils.py
"""

import os
import json
import tempfile
from datetime import datetime
import sys

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import FileManager


def test_last_run_time_bug():
    """Test that demonstrates the last_run_time bug"""
    print("🔍 Testing last_run_time bug in utils.py")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create initial data without last_run_time
            initial_data = {
                "posted_uris": ["test-uri-1", "test-uri-2"],
                "queued_articles": [{"title": "Test Article", "uri": "test-uri-3"}],
                "last_run_time": None
            }
            
            print("1. Saving initial data...")
            FileManager.save_posted_articles(initial_data)
            
            # Check what was actually saved to disk
            with open("posted_articles.json", "r") as f:
                saved_data = json.load(f)
            
            print(f"2. Data saved to disk: {saved_data}")
            print(f"   last_run_time in saved file: {saved_data.get('last_run_time')}")
            print(f"   last_run_time in memory: {initial_data.get('last_run_time')}")
            
            # The bug: last_run_time should be updated but it's not persisted
            if saved_data.get("last_run_time") is None:
                print("❌ BUG CONFIRMED: last_run_time was not saved to disk!")
                print("   The method updated it in memory AFTER saving the file")
                return False
            else:
                print("✅ No bug: last_run_time was properly saved")
                return True
                
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    success = test_last_run_time_bug()
    exit(0 if success else 1)