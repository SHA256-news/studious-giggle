"""
Image Management for Bitcoin Mining News Bot
------------------------------------------
This module handles image selection and library management for enhancing tweets.
"""

import os
import json
import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger('bitcoin_mining_bot')

class ImageHandler:
    """Handles image selection and library management"""
    
    def __init__(self):
        self.images_dir = "images"
        
        # Create images directory if it doesn't exist
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Initialize basic categories
        self.categories = {
            "bitcoin": {"description": "Bitcoin logos, mining equipment", "images": []},
            "mining": {"description": "Mining equipment and operations", "images": []},
            "companies": {"description": "Company logos and corporate imagery", "images": []},
            "countries": {"description": "Country flags and landmarks", "images": []}
        }
        
        self._load_available_images()
    
    def _load_available_images(self):
        """Load available images from the images directory"""
        if not os.path.exists(self.images_dir):
            return
        
        for filename in os.listdir(self.images_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(self.images_dir, filename)
                
                # Categorize images based on filename
                filename_lower = filename.lower()
                if 'bitcoin' in filename_lower or 'btc' in filename_lower:
                    self.categories["bitcoin"]["images"].append(file_path)
                elif 'mining' in filename_lower or 'miner' in filename_lower:
                    self.categories["mining"]["images"].append(file_path)
                elif any(word in filename_lower for word in ['company', 'corp', 'logo']):
                    self.categories["companies"]["images"].append(file_path)
                elif any(word in filename_lower for word in ['flag', 'country']):
                    self.categories["countries"]["images"].append(file_path)
                else:
                    # Default to bitcoin category
                    self.categories["bitcoin"]["images"].append(file_path)
    
    def ensure_basic_images_available(self):
        """Ensure basic Bitcoin images are available"""
        total_images = sum(len(cat["images"]) for cat in self.categories.values())
        if total_images == 0:
            logger.warning("No Bitcoin images available - image functionality may be limited")
        else:
            logger.info(f"Found {total_images} images across {len(self.categories)} categories")
    
    def select_images_for_headline(self, headline: str, max_images: int = 2) -> List[str]:
        """Select appropriate images for a headline"""
        images = []
        headline_lower = headline.lower()
        
        # Try to match images based on headline content
        if 'mining' in headline_lower and self.categories["mining"]["images"]:
            images.extend(random.sample(
                self.categories["mining"]["images"], 
                min(1, len(self.categories["mining"]["images"]))
            ))
        
        # Add Bitcoin images if we have space
        if len(images) < max_images and self.categories["bitcoin"]["images"]:
            bitcoin_images = [img for img in self.categories["bitcoin"]["images"] if img not in images]
            if bitcoin_images:
                images.extend(random.sample(
                    bitcoin_images, 
                    min(max_images - len(images), len(bitcoin_images))
                ))
        
        # Fallback to any available images
        if not images:
            all_images = []
            for category in self.categories.values():
                all_images.extend(category["images"])
            if all_images:
                images.extend(random.sample(all_images, min(max_images, len(all_images))))
        
        logger.info(f"Selected {len(images)} images for headline: {headline}")
        return images[:max_images]
    
    def get_fallback_bitcoin_image(self) -> Optional[str]:
        """Get a fallback Bitcoin image"""
        if self.categories["bitcoin"]["images"]:
            return random.choice(self.categories["bitcoin"]["images"])
        
        # Try other categories as fallback
        for category in self.categories.values():
            if category["images"]:
                return random.choice(category["images"])
        
        return None