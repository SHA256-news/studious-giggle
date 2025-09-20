#!/usr/bin/env python3

"""
Test script for Gemini AI integration functionality
Tests the new AI analysis and report generation features
"""

import os
import sys
import logging
import tempfile
import shutil
from unittest.mock import Mock, patch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_gemini_client_import():
    """Test that Gemini client can be imported"""
    print("Testing Gemini client import...")
    
    try:
        from gemini_client import GeminiClient, ReportGenerator
        print("✓ GeminiClient imported successfully")
        print("✓ ReportGenerator imported successfully")
        return True
    except Exception as e:
        print(f"✗ Gemini client import failed: {e}")
        return False

def test_report_generator():
    """Test report generator functionality"""
    print("\nTesting report generator...")
    
    try:
        from gemini_client import ReportGenerator
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            report_gen = ReportGenerator(temp_dir)
            
            # Test analysis data
            test_analysis = {
                'article_title': 'Test Bitcoin Mining News',
                'article_url': 'https://example.com/test-article',
                'analysis_text': '# Test Analysis\n\nThis is a test analysis of the article.',
                'analysis_timestamp': '2024-01-01T00:00:00',
                'model_used': 'gemini-1.5-flash'
            }
            
            # Generate report
            report_path = report_gen.save_analysis_report(test_analysis)
            
            if report_path and os.path.exists(report_path):
                print(f"✓ Report generated successfully: {os.path.basename(report_path)}")
                
                # Check content
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'Test Bitcoin Mining News' in content and '# Test Analysis' in content:
                        print("✓ Report content is correct")
                        return True
                    else:
                        print("✗ Report content is incorrect")
                        return False
            else:
                print("✗ Report generation failed")
                return False
                
    except Exception as e:
        print(f"✗ Report generator test failed: {e}")
        return False

def test_gemini_config():
    """Test Gemini configuration"""
    print("\nTesting Gemini configuration...")
    
    try:
        from config import GeminiConfig
        
        # Test without API key (should fail)
        try:
            config = GeminiConfig.from_env()
            print("✗ Should have failed without API key")
            return False
        except ValueError as e:
            if "GEMINI_API_KEY" in str(e):
                print("✓ Correctly handles missing API key")
            else:
                print(f"✗ Wrong error message: {e}")
                return False
        
        # Test with API key
        os.environ['GEMINI_API_KEY'] = 'test_key_123'
        try:
            config = GeminiConfig.from_env()
            if config.api_key == 'test_key_123':
                print("✓ Correctly loads API key from environment")
                return True
            else:
                print("✗ API key not loaded correctly")
                return False
        finally:
            # Clean up
            os.environ.pop('GEMINI_API_KEY', None)
            
    except Exception as e:
        print(f"✗ Gemini config test failed: {e}")
        return False

def test_bot_integration():
    """Test that bot can integrate with Gemini functionality"""
    print("\nTesting bot integration...")
    
    try:
        # Mock the Gemini API to avoid actual API calls
        with patch('google.genai.Client'), \
             patch('google.genai.types'):
            
            from bot import BitcoinMiningNewsBot
            from gemini_client import GeminiClient, ReportGenerator
            
            # Test bot initialization in safe mode (no API calls)
            bot = BitcoinMiningNewsBot(safe_mode=True)
            
            if hasattr(bot, 'report_generator') and isinstance(bot.report_generator, ReportGenerator):
                print("✓ Bot has report generator")
            else:
                print("✗ Bot missing report generator")
                return False
            
            if hasattr(bot, '_analyze_and_save_report'):
                print("✓ Bot has analysis method")
            else:
                print("✗ Bot missing analysis method")
                return False
            
            return True
            
    except Exception as e:
        print(f"✗ Bot integration test failed: {e}")
        return False

def test_api_client_manager():
    """Test API client manager with Gemini"""
    print("\nTesting API client manager...")
    
    try:
        from api_clients import APIClientManager
        
        # Test in safe mode
        manager = APIClientManager(safe_mode=True)
        
        if hasattr(manager, 'gemini_client'):
            print("✓ API manager has gemini_client attribute")
        else:
            print("✗ API manager missing gemini_client attribute")
            return False
        
        if hasattr(manager, 'get_gemini_client'):
            print("✓ API manager has get_gemini_client method")
        else:
            print("✗ API manager missing get_gemini_client method")
            return False
        
        # Test getting Gemini client (should be None in safe mode)
        gemini_client = manager.get_gemini_client()
        if gemini_client is None:
            print("✓ Gemini client is None in safe mode (expected)")
            return True
        else:
            print("✗ Gemini client should be None in safe mode")
            return False
            
    except Exception as e:
        print(f"✗ API client manager test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini AI Integration")
    print("=" * 50)
    
    success = True
    
    success &= test_gemini_client_import()
    success &= test_gemini_config()
    success &= test_report_generator()
    success &= test_api_client_manager()
    success &= test_bot_integration()
    
    if success:
        print("\n🎉 All Gemini integration tests passed!")
        print("\nThe following features are working:")
        print("  - Gemini AI client integration")
        print("  - Configuration management for GEMINI_API_KEY")
        print("  - Report generation and saving")
        print("  - Bot integration with analysis pipeline")
        print("  - API client manager with Gemini support")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)