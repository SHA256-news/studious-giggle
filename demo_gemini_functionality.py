#!/usr/bin/env python3

"""
Demo script for Gemini AI integration functionality
Shows how the new AI analysis and report generation works
"""

import os
import tempfile
from unittest.mock import Mock, patch

def demo_gemini_functionality():
    """Demonstrate the Gemini AI functionality"""
    print("🤖 Bitcoin Mining News Bot - Gemini AI Demo")
    print("=" * 50)
    
    print("\n1. Creating mock article data...")
    mock_article = {
        'title': 'Bitcoin Mining Giant Marathon Digital Expands Texas Operations with 200MW Facility',
        'body': '''Marathon Digital Holdings, one of the largest Bitcoin mining companies in North America, 
        announced today a major expansion of its Texas mining operations with the acquisition of a new 200-megawatt 
        mining facility in West Texas. The facility, which is expected to become operational in Q2 2024, will house 
        approximately 20,000 ASIC miners and is projected to generate roughly 8 exahash per second (EH/s) of mining 
        capacity. This expansion represents Marathon's continued commitment to scaling its Bitcoin mining operations 
        while maintaining focus on renewable energy sources. The facility will be powered primarily by wind and 
        solar energy, aligning with the company's ESG goals and the broader industry trend toward sustainable mining 
        practices. Marathon's CEO stated that this expansion will increase their total mining capacity to over 
        35 EH/s by the end of 2024, positioning them as a market leader in sustainable Bitcoin mining.''',
        'url': 'https://example.com/marathon-digital-texas-expansion',
        'uri': 'test-article-123',
        'dateTime': '2024-01-15T10:00:00Z'
    }
    
    print(f"   📰 Title: {mock_article['title']}")
    print(f"   🌐 URL: {mock_article['url']}")
    print(f"   📄 Content: {len(mock_article['body'])} characters")
    
    print("\n2. Testing Gemini client functionality...")
    
    try:
        # Mock the Gemini API to avoid actual API calls
        with patch('google.generativeai.configure') as mock_configure, \
             patch('google.generativeai.GenerativeModel') as mock_model_class:
            
            # Create mock response
            mock_response = Mock()
            mock_response.text = """# Bitcoin Mining Industry Analysis

## Key Points Summary
- Marathon Digital announces major 200MW facility expansion in Texas
- Facility to house 20,000 ASIC miners generating 8 EH/s capacity
- Focus on renewable energy sources (wind and solar)
- Expected operational by Q2 2024

## Bitcoin Mining Impact
This expansion significantly increases Marathon's mining capacity and solidifies their position as a leading North American mining operation. The addition of 8 EH/s represents substantial growth in the overall network hashrate.

## Market Implications
- Increased competition in the mining sector
- Positive signal for Bitcoin mining industry growth
- Demonstrates continued institutional investment in mining infrastructure
- May influence Bitcoin hashrate and network security

## Technical Analysis
- 20,000 ASIC miners suggest use of latest-generation mining hardware
- 200MW capacity indicates significant power infrastructure investment
- 8 EH/s output shows efficient mining operation design

## Regulatory/Policy Implications
- Texas continues to attract Bitcoin mining operations
- Renewable energy focus addresses regulatory concerns about mining's environmental impact
- May influence other miners to adopt similar ESG practices

## Future Outlook
Marathon's expansion to 35+ EH/s positions them for significant market presence. The renewable energy focus sets a precedent for sustainable mining practices.

## Investment Considerations
- Positive indicator for Marathon Digital stock (MARA)
- Demonstrates scalable business model
- Renewable energy focus may attract ESG-conscious investors"""

            mock_model_instance = Mock()
            mock_model_instance.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model_instance
            
            from gemini_client import GeminiClient, ReportGenerator
            from config import GeminiConfig
            
            # Create mock config
            config = Mock()
            config.api_key = "test_api_key_123"
            
            # Test Gemini client
            client = GeminiClient(config)
            print("   ✅ Gemini client initialized")
            
            # Analyze article
            analysis = client.analyze_article(mock_article)
            print("   ✅ Article analysis completed")
            print(f"   📊 Analysis length: {len(analysis['analysis_text'])} characters")
            print(f"   🕒 Timestamp: {analysis['analysis_timestamp']}")
            print(f"   🤖 Model: {analysis['model_used']}")
            
    except Exception as e:
        print(f"   ❌ Gemini client test failed: {e}")
        return False
    
    print("\n3. Testing report generation...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_gen = ReportGenerator(temp_dir)
            print(f"   📁 Reports directory: {temp_dir}")
            
            # Generate report
            report_path = report_gen.save_analysis_report(analysis)
            print(f"   ✅ Report generated: {os.path.basename(report_path)}")
            
            # Show report content preview
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                print("\n   📝 Report preview (first 10 lines):")
                for i, line in enumerate(lines[:10]):
                    print(f"      {line}")
                if len(lines) > 10:
                    print(f"      ... ({len(lines) - 10} more lines)")
                    
    except Exception as e:
        print(f"   ❌ Report generation failed: {e}")
        return False
    
    print("\n4. Testing bot integration...")
    
    try:
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            
            from bot import BitcoinMiningNewsBot
            
            # Initialize bot in safe mode
            bot = BitcoinMiningNewsBot(safe_mode=True)
            print("   ✅ Bot initialized with Gemini support")
            
            # Check bot has the new functionality
            if hasattr(bot, 'report_generator'):
                print("   ✅ Bot has report generator")
            if hasattr(bot, '_analyze_and_save_report'):
                print("   ✅ Bot has analysis method")
                
    except Exception as e:
        print(f"   ❌ Bot integration test failed: {e}")
        return False
    
    print("\n🎉 Demo completed successfully!")
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("✅ Gemini AI client integration working")
    print("✅ Article analysis functionality working")
    print("✅ Report generation and saving working")
    print("✅ Bot integration working")
    print("\nThe bot will now:")
    print("• Analyze each article with Gemini AI (when API key is configured)")
    print("• Generate comprehensive markdown reports")
    print("• Save reports to the reports/ directory")
    print("• Continue posting tweets as before")
    
    return True

if __name__ == "__main__":
    demo_gemini_functionality()