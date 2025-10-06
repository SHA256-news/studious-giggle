#!/usr/bin/env python3
"""
Test script to check what Gemini is actually generating for headlines.
This will help us debug the headline quality issue.
"""

import sys
import os
sys.path.insert(0, '/workspaces/studious-giggle')

from core import Article, GeminiClient

def test_gemini_headlines():
    """Test Gemini headline generation with some sample articles."""
    print("🧪 Testing Gemini Headline Generation")
    print("=" * 50)
    
    # Test articles (based on recent real examples)
    test_articles = [
        {
            'title': 'HIVE Digital Technologies (NASDAQ: HIVE) shares hit a 52-week high',
            'url': 'https://example.com/hive-digital-news',
            'body': 'HIVE Digital Technologies stock reached new highs as Bitcoin mining profitability increased. The company operates mining facilities in Canada and is expanding operations.',
            'source': {'title': 'Crypto News'}
        },
        {
            'title': 'Cipher Mining at H.C. Wainwright: Strategic Insights into Bitcoin and AI',
            'url': 'https://www.investing.com/news/transcripts/cipher-mining-at-hc-wainwright-strategic-insights-into-bitcoin-and-ai-93CH-4232405',
            'body': 'Cipher Mining discussed strategic positioning in Bitcoin mining and AI data centers, focusing on integrating high-performance computing capabilities.',
            'source': {'title': 'Investing.com'}
        }
    ]
    
    # Mock Gemini client (we don't have real API key)
    try:
        gemini = GeminiClient("test-key")
        print("✅ GeminiClient initialized")
        
        for i, article_data in enumerate(test_articles, 1):
            print(f"\n📰 Test Article {i}:")
            print(f"Original Title: {article_data['title']}")
            print(f"URL: {article_data['url']}")
            
            # Create article object
            article = Article.from_dict(article_data)
            
            # Test what prompt is being sent
            print(f"\n🎯 Testing headline generation...")
            try:
                # This will fail without real API key, but we can see the prompt
                headline = gemini.generate_catchy_headline(article)
                print(f"Generated Headline: {headline}")
            except Exception as e:
                print(f"Expected error (no API key): {e}")
                # Show what the prompt would be
                print(f"\n📝 Prompt being sent to Gemini:")
                prompt = f"""
Create a compelling, newsworthy headline for this Bitcoin mining article at {article.url}

Use the full article content to understand the complete story, then create a headline that:
- Captures the MAIN story/takeaway with specific details from the article
- NO emojis, hashtags, or special characters
- 60-80 characters maximum  
- Include specific numbers, percentages, or key facts when available
- Use action words like "surges", "drops", "reaches", "announces", "adopts"

Return only the headline text, nothing else.
"""
                print(prompt.strip())
            
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ Error setting up test: {e}")

if __name__ == "__main__":
    test_gemini_headlines()