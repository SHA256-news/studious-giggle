"""
Image Selection for Bitcoin Mining News Bot
------------------------------------------
This module selects appropriate images for tweets based on headline analysis.
"""

import random
import logging
from typing import List, Optional, Tuple
from image_library import ImageLibrary
from entity_extractor import EntityExtractor

logger = logging.getLogger('image_selector')

class ImageSelector:
    """Selects appropriate images for Bitcoin news tweets"""
    
    def __init__(self):
        self.image_library = ImageLibrary()
        self.entity_extractor = EntityExtractor()
        
        # Ensure basic images are available
        self.image_library.ensure_basic_images_available()
    
    def select_images_for_headline(self, headline: str) -> List[str]:
        """Select up to 2 images for a headline: entity-specific + Bitcoin-related"""
        images = []
        
        try:
            # Analyze the headline
            analysis = self.entity_extractor.analyze_headline(headline)
            
            # Get entity-specific image first (higher priority)
            entity_image = self._get_entity_image(analysis)
            if entity_image:
                images.append(entity_image)
                logger.info(f"Selected entity image: {entity_image}")
            
            # Get Bitcoin-related image second
            bitcoin_image = self._get_bitcoin_image(analysis, exclude=images)
            if bitcoin_image:
                images.append(bitcoin_image)
                logger.info(f"Selected Bitcoin image: {bitcoin_image}")
            
            # If we don't have any images, try to get at least one Bitcoin image
            if not images:
                fallback_image = self._get_fallback_bitcoin_image()
                if fallback_image:
                    images.append(fallback_image)
                    logger.info(f"Selected fallback Bitcoin image: {fallback_image}")
            
            logger.info(f"Selected {len(images)} images for headline: {headline[:50]}...")
            return images
            
        except Exception as e:
            logger.error(f"Error selecting images for headline: {str(e)}")
            # Try to return at least a fallback Bitcoin image
            fallback = self._get_fallback_bitcoin_image()
            return [fallback] if fallback else []
    
    def _get_entity_image(self, analysis: dict) -> Optional[str]:
        """Get image for the primary entity in the headline"""
        primary_entity = analysis.get('primary_entity', {})
        entity_type = primary_entity.get('type')
        entity_value = primary_entity.get('value')
        
        if not entity_type or not entity_value:
            return None
        
        # Try to get specific entity image
        return self.image_library.get_entity_image(entity_value, entity_type)
    
    def _get_bitcoin_image(self, analysis: dict, exclude: List[str] = None) -> Optional[str]:
        """Get appropriate Bitcoin image based on context"""
        if exclude is None:
            exclude = []
        
        bitcoin_context = analysis.get('bitcoin_context', 'general')
        
        # Get available Bitcoin images
        bitcoin_images = self.image_library.get_bitcoin_images()
        
        # Filter out already selected images
        available_images = [img for img in bitcoin_images if img not in exclude]
        
        if not available_images:
            return None
        
        # For now, just return a random Bitcoin image
        # In the future, we could be more context-specific
        return random.choice(available_images)
    
    def _get_fallback_bitcoin_image(self) -> Optional[str]:
        """Get a fallback Bitcoin image when no other images are available"""
        bitcoin_images = self.image_library.get_bitcoin_images()
        if bitcoin_images:
            return random.choice(bitcoin_images)
        return None
    
    def validate_images_for_twitter(self, image_paths: List[str]) -> List[str]:
        """Validate that images meet Twitter requirements"""
        valid_images = []
        
        for image_path in image_paths:
            if self._is_valid_twitter_image(image_path):
                valid_images.append(image_path)
            else:
                logger.warning(f"Image {image_path} doesn't meet Twitter requirements")
        
        return valid_images
    
    def _is_valid_twitter_image(self, image_path: str) -> bool:
        """Check if image meets Twitter requirements"""
        try:
            from PIL import Image
            import os
            
            # Check if file exists
            if not os.path.exists(image_path):
                return False
            
            # Check file size (max 5MB for images)
            file_size = os.path.getsize(image_path)
            if file_size > 5 * 1024 * 1024:  # 5MB
                return False
            
            # Check image dimensions and format
            with Image.open(image_path) as img:
                width, height = img.size
                
                # Twitter max dimensions: 4096x4096
                if width > 4096 or height > 4096:
                    return False
                
                # Check format (Twitter supports JPEG, PNG, GIF, WebP)
                if img.format not in ['JPEG', 'PNG', 'GIF', 'WEBP']:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating image {image_path}: {str(e)}")
            return False