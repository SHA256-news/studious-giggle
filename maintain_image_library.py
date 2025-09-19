#!/usr/bin/env python3
"""
Image Library Maintenance Script
--------------------------------
This script proactively downloads and maintains the image library for the Bitcoin Mining News Bot.
It runs as part of GitHub Actions to ensure images are always available and up-to-date.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Tuple, Optional
from image_library import ImageLibrary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('image_maintenance')

class ImageLibraryMaintenance:
    """Manages automated maintenance of the image library"""
    
    def __init__(self):
        self.image_library = ImageLibrary()
        self.maintenance_report = {
            "images_processed": 0,
            "images_downloaded": 0,
            "images_updated": 0,
            "images_failed": 0,
            "broken_urls": [],
            "new_images": [],
            "updated_images": []
        }
    
    def maintain_bitcoin_images(self) -> bool:
        """Download and maintain core Bitcoin images"""
        logger.info("Maintaining Bitcoin images...")
        success = True
        
        for img_config in self.image_library.library_config.get("default_bitcoin_images", []):
            self.maintenance_report["images_processed"] += 1
            
            name = img_config.get("name", "unknown")
            url = img_config.get("url")
            current_path = img_config.get("local_path")
            
            if not url:
                logger.warning(f"No URL configured for Bitcoin image: {name}")
                continue
            
            filename = f"bitcoin_{name}.png"
            local_path = os.path.join(self.image_library.images_dir, filename)
            
            # Check if image needs downloading/updating
            needs_download = False
            if not current_path or not os.path.exists(current_path):
                needs_download = True
                logger.info(f"Bitcoin image {name} not found locally, downloading...")
            elif current_path != local_path:
                needs_download = True
                logger.info(f"Bitcoin image {name} path mismatch, re-downloading...")
            
            if needs_download:
                downloaded_path = self.image_library.download_image(url, filename)
                if downloaded_path:
                    img_config["local_path"] = downloaded_path
                    self.maintenance_report["images_downloaded"] += 1
                    self.maintenance_report["new_images"].append(f"bitcoin/{name}")
                    logger.info(f"✓ Downloaded Bitcoin image: {name}")
                else:
                    self.maintenance_report["images_failed"] += 1
                    self.maintenance_report["broken_urls"].append(f"bitcoin/{name}: {url}")
                    logger.error(f"✗ Failed to download Bitcoin image: {name}")
                    success = False
        
        # Save updated configuration
        self.image_library._save_library_config(self.image_library.library_config)
        return success
    
    def maintain_entity_images(self) -> bool:
        """Download and maintain entity-specific images"""
        logger.info("Maintaining entity images...")
        success = True
        
        for entity_type, entities in self.image_library.entity_mapping.items():
            logger.info(f"Processing {entity_type} entities...")
            
            for entity_name, entity_config in entities.items():
                self.maintenance_report["images_processed"] += 1
                
                url = entity_config.get("image_url")
                current_path = entity_config.get("local_path")
                
                if not url:
                    logger.warning(f"No URL configured for {entity_type}/{entity_name}")
                    continue
                
                filename = f"{entity_type}_{entity_name.replace(' ', '_')}.png"
                local_path = os.path.join(self.image_library.images_dir, filename)
                
                # Check if image needs downloading/updating
                needs_download = False
                if not current_path or not os.path.exists(current_path):
                    needs_download = True
                    logger.info(f"Entity image {entity_type}/{entity_name} not found locally, downloading...")
                elif current_path != local_path:
                    needs_download = True
                    logger.info(f"Entity image {entity_type}/{entity_name} path mismatch, re-downloading...")
                
                if needs_download:
                    downloaded_path = self.image_library.download_image(url, filename)
                    if downloaded_path:
                        entity_config["local_path"] = downloaded_path
                        self.maintenance_report["images_downloaded"] += 1
                        self.maintenance_report["new_images"].append(f"{entity_type}/{entity_name}")
                        logger.info(f"✓ Downloaded entity image: {entity_type}/{entity_name}")
                    else:
                        self.maintenance_report["images_failed"] += 1
                        self.maintenance_report["broken_urls"].append(f"{entity_type}/{entity_name}: {url}")
                        logger.error(f"✗ Failed to download entity image: {entity_type}/{entity_name}")
                        success = False
        
        # Save updated entity mapping
        self.image_library._save_entity_mapping(self.image_library.entity_mapping)
        return success
    
    def validate_existing_images(self) -> bool:
        """Validate that all referenced images actually exist"""
        logger.info("Validating existing images...")
        issues_found = False
        
        # Check Bitcoin images
        for img_config in self.image_library.library_config.get("default_bitcoin_images", []):
            local_path = img_config.get("local_path")
            if local_path and not os.path.exists(local_path):
                logger.warning(f"Bitcoin image missing: {local_path}")
                img_config["local_path"] = None
                issues_found = True
                self.maintenance_report["updated_images"].append(f"bitcoin/{img_config.get('name', 'unknown')} - marked as missing")
        
        # Check entity images
        for entity_type, entities in self.image_library.entity_mapping.items():
            for entity_name, entity_config in entities.items():
                local_path = entity_config.get("local_path")
                if local_path and not os.path.exists(local_path):
                    logger.warning(f"Entity image missing: {entity_type}/{entity_name} -> {local_path}")
                    entity_config["local_path"] = None
                    issues_found = True
                    self.maintenance_report["updated_images"].append(f"{entity_type}/{entity_name} - marked as missing")
        
        if issues_found:
            self.image_library._save_library_config(self.image_library.library_config)
            self.image_library._save_entity_mapping(self.image_library.entity_mapping)
            self.maintenance_report["images_updated"] += 1
        
        return not issues_found
    
    def generate_maintenance_report(self) -> Dict:
        """Generate a comprehensive maintenance report"""
        # Count available images
        available_bitcoin = len(self.image_library.get_bitcoin_images())
        available_entities = 0
        
        for entity_type, entities in self.image_library.entity_mapping.items():
            for entity_name, entity_config in entities.items():
                if entity_config.get("local_path") and os.path.exists(entity_config["local_path"]):
                    available_entities += 1
        
        report = {
            **self.maintenance_report,
            "summary": {
                "total_available_images": available_bitcoin + available_entities,
                "available_bitcoin_images": available_bitcoin,
                "available_entity_images": available_entities,
                "total_configured_entities": sum(len(entities) for entities in self.image_library.entity_mapping.values()),
                "total_configured_bitcoin": len(self.image_library.library_config.get("default_bitcoin_images", []))
            }
        }
        
        return report
    
    def run_maintenance(self) -> bool:
        """Run complete image library maintenance"""
        logger.info("🖼️  Starting image library maintenance...")
        logger.info("=" * 60)
        
        try:
            # Validate existing images first
            logger.info("Step 1: Validating existing images...")
            self.validate_existing_images()
            
            # Maintain Bitcoin images
            logger.info("Step 2: Maintaining Bitcoin images...")
            bitcoin_success = self.maintain_bitcoin_images()
            
            # Maintain entity images
            logger.info("Step 3: Maintaining entity images...")
            entity_success = self.maintain_entity_images()
            
            # Generate report
            report = self.generate_maintenance_report()
            
            # Log summary
            logger.info("=" * 60)
            logger.info("🎯 Maintenance Summary:")
            logger.info(f"  📊 Images processed: {report['images_processed']}")
            logger.info(f"  ⬇️  Images downloaded: {report['images_downloaded']}")
            logger.info(f"  🔄 Images updated: {report['images_updated']}")
            logger.info(f"  ❌ Images failed: {report['images_failed']}")
            logger.info(f"  🏆 Total available: {report['summary']['total_available_images']}")
            logger.info(f"     - Bitcoin: {report['summary']['available_bitcoin_images']}")
            logger.info(f"     - Entities: {report['summary']['available_entity_images']}")
            
            if report['new_images']:
                logger.info(f"  🆕 New images: {', '.join(report['new_images'])}")
            
            if report['broken_urls']:
                logger.warning(f"  🔗 Broken URLs: {len(report['broken_urls'])}")
                for broken_url in report['broken_urls']:
                    logger.warning(f"    - {broken_url}")
            
            # Save report
            with open('image_maintenance_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            success = bitcoin_success and entity_success
            
            if success:
                logger.info("✅ Image library maintenance completed successfully!")
            else:
                logger.error("❌ Image library maintenance completed with errors!")
            
            return success
            
        except Exception as e:
            logger.error(f"💥 Image library maintenance failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main entry point"""
    maintenance = ImageLibraryMaintenance()
    success = maintenance.run_maintenance()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()