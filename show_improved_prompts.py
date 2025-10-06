#!/usr/bin/env python3
"""
Show the improved Gemini prompts for headline and summary generation.
"""

def show_improved_prompts():
    """Show the new, much better prompts that will generate catchy headlines."""
    print("🎯 IMPROVED GEMINI PROMPTS")
    print("=" * 60)
    
    print("\n📰 NEW HEADLINE PROMPT:")
    print("-" * 30)
    headline_prompt = """
Read the Bitcoin mining article at {article_url} and write a PUNCHY news headline.

CRITICAL REQUIREMENTS:
- Write like a professional financial news reporter
- Start with COMPANY NAME or KEY ACTION, never "The article states that..."
- Keep it under 70 characters
- Include specific numbers, percentages, or dollar amounts from the article
- Use powerful action verbs: "soars", "plummets", "hits", "reaches", "secures", "reports"
- Sound like headlines from Bloomberg, Reuters, or MarketWatch

GOOD EXAMPLES:
- "HIVE Hits 52-Week High on Mining Surge"
- "Riot Platforms Acquires 5,000 Bitcoin Miners"
- "Marathon Digital Reports Record Q3 Revenue"
- "CleanSpark Stock Jumps 15% on Expansion News"

BAD EXAMPLES (NEVER DO THIS):
- "The article states that HIVE Digital Technologies..."
- "According to the report, Marathon Digital..."
- "The company announced in the article..."

Return ONLY the headline, no quotes, no explanation.
    """
    print(headline_prompt.strip())
    
    print("\n📋 NEW SUMMARY PROMPT:")
    print("-" * 30)
    summary_prompt = """
Read the full Bitcoin mining article at {article_url} and create SPECIFIC bullet points.

Generated Headline: {headline}

CRITICAL: DO NOT repeat anything from the headline above.

Create 3 rapid-fire bullet points that reveal NEW details from the article:
- Total length under 180 characters
- Include specific numbers, dates, locations, dollar amounts from the article
- Use telegraphic style like financial newswires
- Each point 50-60 characters max
- Format: "• [specific fact]"
- NO generic statements

GOOD EXAMPLES:
• Q3 revenue jumped 42% to $87M year-over-year
• Added 2,500 miners at Texas facility this month  
• Power costs dropped to 4.2¢/kWh from 6.1¢/kWh

BAD EXAMPLES (NEVER DO):
• The company is performing well
• Bitcoin mining operations are expanding
• Management is optimistic about the future

Return ONLY the bullet points, nothing else.
    """
    print(summary_prompt.strip())
    
    print("\n🎉 EXPECTED IMPROVEMENTS:")
    print("-" * 30)
    print("❌ OLD: 'The article states that HIVE Digital Technologies (NASDAQ: HIVE) shares hit a 52'")
    print("✅ NEW: 'HIVE Hits 52-Week High on Mining Surge'")
    print()
    print("❌ OLD: Generic, robotic language")
    print("✅ NEW: Punchy, specific, action-oriented headlines")
    print()
    print("❌ OLD: Wasted characters on '(NASDAQ: HIVE)'")
    print("✅ NEW: More space for the actual news")
    print()
    print("❌ OLD: Starting with 'The article states that...'")
    print("✅ NEW: Starting with company name or action")

if __name__ == "__main__":
    show_improved_prompts()