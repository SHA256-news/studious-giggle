#!/usr/bin/env python3
"""
Image Functionality Demo
------------------------
This script demonstrates the new image attachment functionality
for the Bitcoin Mining News Bot.
"""

import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def demo_entity_extraction():
    """Demonstrate entity extraction from headlines"""
    print("=" * 60)
    print("DEMO: Entity Extraction from Headlines")
    print("=" * 60)
    
    from entity_extractor import EntityExtractor
    extractor = EntityExtractor()
    
    # Demo headlines with various entities
    demo_headlines = [
        "Michigan Bitcoin Reserve Bill Moves Forward After Months of Delay",
        "Texas Bitcoin Mining Farm Expands Operations with 100 New Rigs", 
        "Coinbase Announces New Bitcoin Mining Support Features",
        "SEC Approves First Bitcoin Mining ETF Application",
        "China Bans Bitcoin Mining Operations Nationwide",
        "MicroStrategy Adds 1,000 More Bitcoin to Treasury Holdings",
        "Bitcoin Mining Difficulty Reaches All-Time High",
        "California Proposes Bitcoin Mining Regulations",
        "Riot Blockchain Reports Q3 Mining Revenue Growth"
    ]
    
    for headline in demo_headlines:
        print(f"\nHeadline: {headline}")
        analysis = extractor.analyze_headline(headline)
        
        entities = analysis['entities']
        primary = analysis['primary_entity']
        context = analysis['bitcoin_context']
        
        print(f"  📍 Locations: {', '.join(entities['locations']) or 'None'}")
        print(f"  🏢 Companies: {', '.join(entities['companies']) or 'None'}")
        print(f"  🏛️  Regulatory: {', '.join(entities['regulatory']) or 'None'}")
        print(f"  💡 Concepts: {', '.join(entities['concepts']) or 'None'}")
        print(f"  🎯 Primary Entity: {primary['type']} = {primary['value']}")
        print(f"  📊 Bitcoin Context: {context}")

def demo_image_selection():
    """Demonstrate image selection for headlines"""
    print("\n" + "=" * 60)
    print("DEMO: Image Selection for Headlines")
    print("=" * 60)
    
    from image_selector import ImageSelector
    selector = ImageSelector()
    
    demo_headlines = [
        "Michigan Bitcoin Reserve Bill Moves Forward",
        "Texas Bitcoin Mining Farm Expansion Announced",
        "Coinbase Launches New Mining Services",
        "SEC Approves Bitcoin ETF Application"
    ]
    
    for headline in demo_headlines:
        print(f"\nHeadline: {headline}")
        images = selector.select_images_for_headline(headline)
        print(f"  🖼️  Selected Images ({len(images)}):")
        for i, image_path in enumerate(images, 1):
            print(f"    {i}. {image_path}")
        
        if not images:
            print("    No images selected")

def demo_image_library():
    """Demonstrate image library management"""
    print("\n" + "=" * 60)
    print("DEMO: Image Library Management")
    print("=" * 60)
    
    from image_library import ImageLibrary
    library = ImageLibrary()
    
    print("Image Library Configuration:")
    print(f"  📁 Images Directory: {library.images_dir}")
    print(f"  📝 Config File: {library.library_config_file}")
    print(f"  🗺️  Entity Mapping: {library.entity_mapping_file}")
    
    # Show available Bitcoin images
    bitcoin_images = library.get_bitcoin_images()
    print(f"\n🔸 Available Bitcoin Images ({len(bitcoin_images)}):")
    for image in bitcoin_images:
        print(f"  - {image}")
    
    # Show available entity images
    print(f"\n🗺️  Available Entity Images:")
    test_entities = [
        ("michigan", "locations"),
        ("texas", "locations"),
        ("coinbase", "companies"),
        ("sec", "regulatory")
    ]
    
    for entity, entity_type in test_entities:
        image = library.get_entity_image(entity, entity_type)
        status = "✅ Available" if image else "❌ Not Available"
        print(f"  - {entity_type}/{entity}: {status}")
        if image:
            print(f"    Path: {image}")

def demo_full_workflow():
    """Demonstrate the complete image workflow"""
    print("\n" + "=" * 60)
    print("DEMO: Complete Image Workflow")
    print("=" * 60)
    
    from image_selector import ImageSelector
    selector = ImageSelector()
    
    # Example headline
    headline = "Michigan Bitcoin Reserve Bill Approved by State Senate"
    print(f"Headline: {headline}\n")
    
    # Step 1: Entity Extraction
    print("Step 1: Entity Extraction")
    analysis = selector.entity_extractor.analyze_headline(headline)
    print(f"  Primary Entity: {analysis['primary_entity']['type']} = {analysis['primary_entity']['value']}")
    print(f"  Bitcoin Context: {analysis['bitcoin_context']}")
    
    # Step 2: Image Selection
    print("\nStep 2: Image Selection")
    images = selector.select_images_for_headline(headline)
    print(f"  Selected {len(images)} images:")
    for i, image in enumerate(images, 1):
        print(f"    {i}. {image}")
    
    # Step 3: Image Validation
    print("\nStep 3: Image Validation")
    valid_images = selector.validate_images_for_twitter(images)
    print(f"  {len(valid_images)} images pass Twitter validation")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"  - Entities extracted: ✅")
    print(f"  - Images selected: {len(images)}")
    print(f"  - Images validated: {len(valid_images)}")
    print(f"  - Ready for Twitter: {'✅' if valid_images else '❌'}")

def main():
    """Run all demos"""
    print("🎨 Bitcoin Mining News Bot - Image Functionality Demo")
    print("This demo shows how the new image attachment feature works.")
    
    try:
        demo_entity_extraction()
        demo_image_selection()
        demo_image_library()
        demo_full_workflow()
        
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("=" * 60)
        print("\nThe image functionality provides:")
        print("  🎯 Smart entity extraction from headlines")
        print("  🖼️  Automatic image selection (entity + Bitcoin imagery)")
        print("  📁 Automated image library management")
        print("  ✅ Twitter compatibility validation")
        print("  🔄 Graceful fallback to text-only tweets")
        print("\nImages will be automatically attached to tweets when the bot runs.")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()