#!/usr/bin/env python3
"""
Demo script showing the enhanced tweet formatting with real-world examples
"""

from utils import TextUtils


def demo_enhanced_tweets():
    """Demonstrate the enhanced tweet functionality with realistic examples"""
    print("🚀 Enhanced Tweet Formatting Demo")
    print("=" * 80)
    
    # Real-world test cases inspired by actual Bitcoin mining news
    test_cases = [
        {
            "title": "200 BTC Annually: Hong Kong's Investment Holding Company Sets To Bitcoin Mining",
            "body": "DL Holdings, a Hong Kong-based investment holding company, has announced a $21.85 million investment in Bitcoin mining operations through a bond agreement with Fortune Peak. The company expects to generate approximately 200 BTC annually from their planned deployment of over 2,200 mining rigs.",
            "description": "🏢 Company Investment (Original Problem Example)"
        },
        {
            "title": "CleanSpark Expands Bitcoin Mining Operations with $50 Million Investment in New Facility",
            "body": "CleanSpark Inc has announced a major expansion of its Bitcoin mining operations with a $50 million investment in a new facility in Texas. The facility will house over 3,000 mining rigs and is expected to increase the company's hashrate by 15 EH/s.",
            "description": "📈 Mining Expansion"
        },
        {
            "title": "SEC Approves First Bitcoin Mining ETF for Institutional Investors",
            "body": "The Securities and Exchange Commission has given approval for the first Bitcoin mining exchange-traded fund, marking a significant milestone for institutional investment in the cryptocurrency mining sector.",
            "description": "🏛️ Regulatory Approval"
        },
        {
            "title": "Marathon Digital and Riot Platforms Announce Strategic Partnership for Renewable Energy Mining",
            "body": "Marathon Digital Holdings and Riot Platforms have announced a strategic partnership to develop renewable energy-powered Bitcoin mining operations worth $100 million. The partnership will focus on solar and wind energy sources.",
            "description": "🤝 Company Partnership"
        },
        {
            "title": "Texas Bitcoin Mining Farm Reaches 500 BTC Production Milestone",
            "body": "A major Bitcoin mining facility in Texas has reached a significant milestone, producing over 500 BTC since operations began. The facility operates 5,000+ mining rigs with a total hashrate of 25 TH/s.",
            "description": "🎯 Production Milestone"
        },
        {
            "title": "Chinese Bitcoin Mining Company Relocates $200 Million Operations to Kazakhstan",
            "body": "Following regulatory changes in China, a major Bitcoin mining company has announced the relocation of its $200 million mining operations to Kazakhstan. The move involves transferring over 10,000 mining rigs.",
            "description": "🌍 Geographic Relocation"
        }
    ]
    
    print("\nComparing Original vs Enhanced Tweet Formats:")
    print("-" * 80)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print(f"Original Title: {case['title']}")
        
        # Generate original format tweet
        original_tweet = TextUtils.create_original_tweet_text(case)
        
        # Generate enhanced format tweet  
        enhanced_tweet = TextUtils.create_enhanced_tweet_text(case)
        
        print(f"📜 Original: {original_tweet}")
        print(f"✨ Enhanced: {enhanced_tweet}")
        print(f"   Characters: {len(original_tweet)} → {len(enhanced_tweet)} ({'+'*(len(enhanced_tweet) > len(original_tweet))}{abs(len(enhanced_tweet) - len(original_tweet))})")
        
        # Show what information was extracted
        info = TextUtils.extract_key_info(case)
        extracted_info = []
        if info["companies"]:
            extracted_info.append(f"Companies: {', '.join(info['companies'][:2])}")
        if info["financial_amounts"]:
            extracted_info.append(f"Financial: {', '.join(info['financial_amounts'][:2])}")
        if info["technical_specs"]:
            extracted_info.append(f"Tech: {', '.join(info['technical_specs'][:2])}")
        
        if extracted_info:
            print(f"   📊 Extracted: {' | '.join(extracted_info)}")
    
    print("\n" + "=" * 80)
    print("📈 Enhancement Benefits:")
    print("• More specific company names instead of generic descriptions")
    print("• Financial amounts prominently featured")
    print("• Technical specifications included when space allows")
    print("• Strategic use of abbreviations to save characters")
    print("• Structured information prioritization")
    print("• Maintains character limits while maximizing information density")


def demo_abbreviation_system():
    """Demonstrate the abbreviation system"""
    print("\n🔤 Abbreviation System Demo")
    print("=" * 50)
    
    test_texts = [
        "Bitcoin mining company invests 50 million dollars",
        "Investment holding company partners with major firm",
        "Mining operations target 100 Bitcoin per year",
        "Company announces mining expansion with new facility"
    ]
    
    for text in test_texts:
        abbreviated = TextUtils._apply_abbreviations(text)
        savings = len(text) - len(abbreviated)
        print(f"Original:  {text}")
        print(f"Abbreviated: {abbreviated}")
        print(f"Saved: {savings} characters\n")


if __name__ == "__main__":
    demo_enhanced_tweets()
    demo_abbreviation_system()