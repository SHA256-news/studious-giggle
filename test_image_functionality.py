#!/usr/bin/env python3
"""
Test script for image functionality
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_image_modules():
    """Test that image modules can be imported and work"""
    print("Testing image functionality modules...")
    
    try:
        from entity_extractor import EntityExtractor
        print("✓ EntityExtractor imported successfully")
        
        extractor = EntityExtractor()
        
        # Test headline analysis
        test_headlines = [
            "Michigan Bitcoin Reserve Bill Moves Forward After Months of Delay",
            "Texas Bitcoin Mining Farm Expands Operations",
            "Coinbase Adds New Bitcoin Mining Support",
            "SEC Approves New Bitcoin ETF Application"
        ]
        
        for headline in test_headlines:
            analysis = extractor.analyze_headline(headline)
            print(f"✓ Analyzed: {headline[:30]}... -> {analysis['primary_entity']['type']}: {analysis['primary_entity']['value']}")
        
    except Exception as e:
        print(f"✗ EntityExtractor failed: {e}")
        return False
    
    try:
        from image_library import ImageLibrary
        print("✓ ImageLibrary imported successfully")
        
        library = ImageLibrary()
        print(f"✓ ImageLibrary initialized")
        
        # Check if basic configuration files are created
        if os.path.exists("image_library.json"):
            print("✓ image_library.json created")
        if os.path.exists("entity_image_mapping.json"):
            print("✓ entity_image_mapping.json created")
            
    except Exception as e:
        print(f"✗ ImageLibrary failed: {e}")
        return False
    
    try:
        from image_selector import ImageSelector
        print("✓ ImageSelector imported successfully")
        
        selector = ImageSelector()
        print("✓ ImageSelector initialized")
        
        # Test image selection (without actually downloading)
        test_headline = "Michigan Bitcoin Reserve Bill Moves Forward"
        images = selector.select_images_for_headline(test_headline)
        print(f"✓ Selected {len(images)} images for test headline")
        
    except Exception as e:
        print(f"✗ ImageSelector failed: {e}")
        return False
    
    print("\n✅ All image modules working correctly!")
    return True

def test_bot_integration():
    """Test that bot can import image functionality"""
    print("\nTesting bot integration...")
    
    try:
        # Mock environment variables
        os.environ.update({
            'TWITTER_API_KEY': 'test_key',
            'TWITTER_API_SECRET': 'test_secret',
            'TWITTER_ACCESS_TOKEN': 'test_token',
            'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
            'EVENTREGISTRY_API_KEY': 'test_er_key'
        })
        
        from bot import BitcoinMiningNewsBot
        print("✓ Bot imported successfully")
        
        # Test in safe mode
        bot = BitcoinMiningNewsBot(safe_mode=True)
        print("✓ Bot initialized in safe mode")
        
        # Check if image selector is available
        if hasattr(bot, 'image_selector'):
            print(f"✓ Image selector attribute: {bot.image_selector}")
        else:
            print("✗ No image_selector attribute found")
            return False
            
    except Exception as e:
        print(f"✗ Bot integration failed: {e}")
        return False
    
    print("✅ Bot integration working correctly!")
    return True

if __name__ == "__main__":
    success = True
    
    success &= test_image_modules()
    success &= test_bot_integration()
    
    if success:
        print("\n🎉 All tests passed! Image functionality is ready.")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)