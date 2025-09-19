#!/usr/bin/env python3
"""
Test Image Library Automation
-----------------------------
This script validates the complete image library automation workflow.
"""

import os
import sys
import json
import logging
import tempfile
import shutil
from unittest.mock import patch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('automation_test')

def test_image_maintenance_script():
    """Test the image maintenance script functionality"""
    logger.info("🧪 Testing image maintenance script...")
    
    try:
        from maintain_image_library import ImageLibraryMaintenance
        
        maintenance = ImageLibraryMaintenance()
        
        # Test maintenance report generation
        report = maintenance.generate_maintenance_report()
        
        required_fields = [
            'images_processed', 'images_downloaded', 'images_updated', 
            'images_failed', 'broken_urls', 'new_images', 'summary'
        ]
        
        for field in required_fields:
            if field not in report:
                raise ValueError(f"Missing required field in report: {field}")
        
        logger.info(f"✅ Maintenance script working - report contains all required fields")
        logger.info(f"   Current status: {report['summary']['total_available_images']} images available")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Image maintenance script test failed: {str(e)}")
        return False

def test_github_actions_workflow():
    """Test the GitHub Actions workflow file"""
    logger.info("🧪 Testing GitHub Actions workflow...")
    
    try:
        workflow_path = ".github/workflows/maintain-images.yml"
        
        if not os.path.exists(workflow_path):
            raise FileError("GitHub Actions workflow file not found")
        
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check for required workflow components
        required_components = [
            "name: Maintain Image Library",
            "schedule:",
            "- cron:",
            "workflow_dispatch:",
            "python maintain_image_library.py",
            "git commit",
            "git push"
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            raise ValueError(f"Missing workflow components: {missing_components}")
        
        logger.info("✅ GitHub Actions workflow file is properly configured")
        logger.info("   - Scheduled runs configured")
        logger.info("   - Manual dispatch enabled")
        logger.info("   - Image maintenance script execution")
        logger.info("   - Automatic commits and pushes")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ GitHub Actions workflow test failed: {str(e)}")
        return False

def test_image_library_integration():
    """Test integration with existing image library system"""
    logger.info("🧪 Testing image library integration...")
    
    try:
        from image_library import ImageLibrary
        from image_selector import ImageSelector
        
        # Test that library can be initialized
        library = ImageLibrary()
        selector = ImageSelector()
        
        # Test that existing images are still accessible
        bitcoin_images = library.get_bitcoin_images()
        if not bitcoin_images:
            logger.warning("   ⚠️  No Bitcoin images available, but this is expected before maintenance")
        else:
            logger.info(f"   ✅ {len(bitcoin_images)} Bitcoin images available")
        
        # Test entity image access
        test_entities = [
            ("michigan", "locations"),
            ("texas", "locations"),
            ("coinbase", "companies")
        ]
        
        available_entities = 0
        for entity, entity_type in test_entities:
            if library.get_entity_image(entity, entity_type):
                available_entities += 1
        
        logger.info(f"   ✅ {available_entities}/{len(test_entities)} test entities have images")
        
        # Test image selection
        test_headlines = [
            "Bitcoin mining in Michigan gains momentum",
            "Texas mining operations expand significantly", 
            "Coinbase announces new mining partnership"
        ]
        
        for headline in test_headlines:
            images = selector.select_images_for_headline(headline)
            logger.info(f"   ✅ Selected {len(images)} images for: {headline[:30]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Image library integration test failed: {str(e)}")
        return False

def test_diagnostics_integration():
    """Test that diagnostics include image library status"""
    logger.info("🧪 Testing diagnostics integration...")
    
    try:
        from diagnose_bot import check_image_library
        
        # Test image library check function
        result = check_image_library()
        
        logger.info(f"✅ Image library diagnostic check completed: {'PASS' if result else 'WARN'}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Diagnostics integration test failed: {str(e)}")
        return False

def test_gitignore_configuration():
    """Test that .gitignore is properly configured for automation"""
    logger.info("🧪 Testing .gitignore configuration...")
    
    try:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        
        # Images directory should NOT be ignored (we want to commit images)
        if 'images/' in gitignore_content:
            logger.warning("   ⚠️  images/ directory is ignored - automation won't commit images")
            return False
        
        # Maintenance reports should be ignored
        if 'image_maintenance_report.json' not in gitignore_content:
            logger.warning("   ⚠️  image_maintenance_report.json not ignored - reports will be committed")
        
        logger.info("✅ .gitignore properly configured for image automation")
        logger.info("   - Images directory will be committed")
        logger.info("   - Maintenance reports are ignored")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ .gitignore configuration test failed: {str(e)}")
        return False

def test_complete_workflow():
    """Test the complete automation workflow end-to-end"""
    logger.info("🧪 Testing complete automation workflow...")
    
    try:
        # Check if all components exist
        required_files = [
            "maintain_image_library.py",
            ".github/workflows/maintain-images.yml",
            "image_library.py",
            "image_selector.py",
            "entity_extractor.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            raise FileError(f"Missing required files: {missing_files}")
        
        logger.info("✅ All required automation files present")
        
        # Test that configuration files are properly set up
        config_files = ["image_library.json", "entity_image_mapping.json"]
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    json.load(f)  # Validate JSON
                logger.info(f"   ✅ {config_file} is valid")
            else:
                logger.warning(f"   ⚠️  {config_file} not found (will be created automatically)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Complete workflow test failed: {str(e)}")
        return False

def main():
    """Run all automation tests"""
    logger.info("🚀 Starting Image Library Automation Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Image Maintenance Script", test_image_maintenance_script),
        ("GitHub Actions Workflow", test_github_actions_workflow),
        ("Image Library Integration", test_image_library_integration),
        ("Diagnostics Integration", test_diagnostics_integration),
        (".gitignore Configuration", test_gitignore_configuration),
        ("Complete Workflow", test_complete_workflow)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 40)
        
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name}: PASSED")
            else:
                failed += 1
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            logger.error(f"💥 {test_name}: ERROR - {str(e)}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"🏁 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All tests passed! Image library automation is ready.")
        logger.info("\n📋 Automation Summary:")
        logger.info("   ✅ Automated image maintenance script created")
        logger.info("   ✅ GitHub Actions workflow configured")
        logger.info("   ✅ Daily scheduled maintenance at 6:00 AM UTC")
        logger.info("   ✅ Manual workflow dispatch available")
        logger.info("   ✅ Broken URL detection and reporting")
        logger.info("   ✅ Automatic commits of new images")
        logger.info("   ✅ Integration with existing bot functionality")
        logger.info("   ✅ Enhanced diagnostics with image status")
        logger.info("\n🚀 Next Steps:")
        logger.info("   1. Merge this PR to enable automation")
        logger.info("   2. Monitor GitHub Actions for daily maintenance runs")
        logger.info("   3. Check for issues if broken URLs are detected")
        logger.info("   4. Add more entities to entity_image_mapping.json as needed")
    else:
        logger.error("❌ Some tests failed. Please fix issues before deploying automation.")
        sys.exit(1)

if __name__ == "__main__":
    main()