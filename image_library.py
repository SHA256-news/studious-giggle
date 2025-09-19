"""
Image Library Management for Bitcoin Mining News Bot
--------------------------------------------------
This module manages the automated image library for enhancing tweets with relevant visuals.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from PIL import Image
import io

logger = logging.getLogger('image_library')

class ImageLibrary:
    """Manages automated image library for Bitcoin news tweets"""
    
    def __init__(self):
        self.images_dir = "images"
        self.library_config_file = "image_library.json"
        self.entity_mapping_file = "entity_image_mapping.json"
        
        # Create images directory if it doesn't exist
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Load or create library configuration
        self.library_config = self._load_library_config()
        self.entity_mapping = self._load_entity_mapping()
        
    def _load_library_config(self) -> Dict:
        """Load image library configuration"""
        try:
            with open(self.library_config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.info("Image library config not found, creating default configuration")
            default_config = {
                "categories": {
                    "bitcoin": {
                        "description": "Bitcoin logos, mining equipment, price charts",
                        "images": []
                    },
                    "locations": {
                        "description": "US state flags, country flags, landmarks",
                        "images": []
                    },
                    "companies": {
                        "description": "Crypto company logos",
                        "images": []
                    },
                    "regulatory": {
                        "description": "Government agencies, regulatory bodies",
                        "images": []
                    },
                    "concepts": {
                        "description": "Blockchain, security, adoption imagery",
                        "images": []
                    }
                },
                "default_bitcoin_images": [
                    {
                        "name": "bitcoin_logo",
                        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/256px-Bitcoin.svg.png",
                        "description": "Official Bitcoin logo",
                        "local_path": None
                    },
                    # Note: Mining farm image removed due to broken URL
                    # System will fallback to Bitcoin logo when mining images are needed
                ]
            }
            self._save_library_config(default_config)
            return default_config
    
    def _load_entity_mapping(self) -> Dict:
        """Load entity to image mapping"""
        try:
            with open(self.entity_mapping_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.info("Entity mapping not found, creating default mapping")
            default_mapping = {
                "locations": {
                    "michigan": {
                        "type": "state_flag",
                        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Flag_of_Michigan.svg/320px-Flag_of_Michigan.svg.png",
                        "local_path": None
                    },
                    "texas": {
                        "type": "state_flag", 
                        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Flag_of_Texas.svg/320px-Flag_of_Texas.svg.png",
                        "local_path": None
                    },
                    "california": {
                        "type": "state_flag",
                        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Flag_of_California.svg/320px-Flag_of_California.svg.png",
                        "local_path": None
                    },
                    "united states": {
                        "type": "country_flag",
                        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Flag_of_the_United_States.svg/320px-Flag_of_the_United_States.svg.png",
                        "local_path": None
                    },
                    "china": {
                        "type": "country_flag",
                        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Flag_of_the_People%27s_Republic_of_China.svg/320px-Flag_of_the_People%27s_Republic_of_China.svg.png",
                        "local_path": None
                    }
                },
                "companies": {
                    "coinbase": {
                        "type": "company_logo",
                        "image_url": "https://logo.clearbit.com/coinbase.com",
                        "local_path": None
                    },
                    "microstrategy": {
                        "type": "company_logo", 
                        "image_url": "https://logo.clearbit.com/microstrategy.com",
                        "local_path": None
                    }
                },
                "regulatory": {
                    "sec": {
                        "type": "agency_logo",
                        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Seal_of_the_United_States_Securities_and_Exchange_Commission.svg/200px-Seal_of_the_United_States_Securities_and_Exchange_Commission.svg.png",
                        "local_path": None
                    }
                }
            }
            self._save_entity_mapping(default_mapping)
            return default_mapping
    
    def _save_library_config(self, config: Dict):
        """Save library configuration"""
        with open(self.library_config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _save_entity_mapping(self, mapping: Dict):
        """Save entity mapping"""
        with open(self.entity_mapping_file, 'w') as f:
            json.dump(mapping, f, indent=2)
    
    def download_image(self, url: str, filename: str) -> Optional[str]:
        """Download an image from URL and save locally"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Validate it's an image
            img = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if necessary and save as PNG for consistency
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large (max 1024x1024 for Twitter)
            max_size = (1024, 1024)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            local_path = os.path.join(self.images_dir, filename)
            img.save(local_path, 'PNG', optimize=True)
            
            logger.info(f"Downloaded and saved image: {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download image from {url}: {str(e)}")
            return None
    
    def get_bitcoin_images(self) -> List[str]:
        """Get paths to available Bitcoin-related images"""
        bitcoin_images = []
        
        # Check default Bitcoin images
        for img_config in self.library_config.get("default_bitcoin_images", []):
            local_path = img_config.get("local_path")
            if local_path and os.path.exists(local_path):
                bitcoin_images.append(local_path)
            else:
                # Try to download if not available locally
                url = img_config.get("url")
                if url:
                    filename = f"bitcoin_{img_config['name']}.png"
                    downloaded_path = self.download_image(url, filename)
                    if downloaded_path:
                        img_config["local_path"] = downloaded_path
                        bitcoin_images.append(downloaded_path)
                        self._save_library_config(self.library_config)
        
        return bitcoin_images
    
    def get_entity_image(self, entity: str, entity_type: str) -> Optional[str]:
        """Get image path for a specific entity"""
        entity_lower = entity.lower()
        
        # Check in entity mapping
        mapping_section = self.entity_mapping.get(entity_type, {})
        if entity_lower in mapping_section:
            entity_config = mapping_section[entity_lower]
            local_path = entity_config.get("local_path")
            
            if local_path and os.path.exists(local_path):
                return local_path
            else:
                # Try to download
                url = entity_config.get("image_url")
                if url:
                    filename = f"{entity_type}_{entity_lower.replace(' ', '_')}.png"
                    downloaded_path = self.download_image(url, filename)
                    if downloaded_path:
                        entity_config["local_path"] = downloaded_path
                        self._save_entity_mapping(self.entity_mapping)
                        return downloaded_path
        
        return None
    
    def ensure_basic_images_available(self):
        """Ensure basic Bitcoin images are downloaded and available"""
        logger.info("Ensuring basic Bitcoin images are available...")
        bitcoin_images = self.get_bitcoin_images()
        if bitcoin_images:
            logger.info(f"Found {len(bitcoin_images)} Bitcoin images available")
        else:
            logger.warning("No Bitcoin images available - image functionality may be limited")