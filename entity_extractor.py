"""
Entity Extraction for Bitcoin Mining News Bot
Simplified entity extraction for basic analysis
"""

import re
import logging
from typing import Dict, List

logger = logging.getLogger('bitcoin_mining_bot')

class EntityExtractor:
    """Simplified entity extraction for Bitcoin news headlines"""
    
    def __init__(self):
        # Basic Bitcoin mining concepts
        self.mining_concepts = {
            'mining', 'miner', 'miners', 'hashrate', 'hash rate', 'difficulty',
            'asic', 'rig', 'pool', 'mining pool', 'energy', 'power', 'kwh'
        }
        
        # Common Bitcoin companies
        self.bitcoin_companies = {
            'microstrategy', 'tesla', 'marathon', 'riot', 'core scientific',
            'hive', 'bitfarms', 'argo', 'hut 8', 'canaan', 'bitmain',
            'antminer', 'whatsminer', 'coinbase', 'binance'
        }
        
        # Financial terms
        self.financial_terms = {
            'million', 'billion', 'trillion', 'investment', 'funding',
            'revenue', 'profit', 'loss', 'market cap', 'price', 'cost'
        }
    
    def analyze_headline(self, headline: str) -> Dict[str, any]:
        """Simple headline analysis for image selection"""
        headline_lower = headline.lower()
        
        # Detect main concepts
        concepts = []
        if any(term in headline_lower for term in self.mining_concepts):
            concepts.append('mining')
        if any(term in headline_lower for term in self.bitcoin_companies):
            concepts.append('companies')
        if any(term in headline_lower for term in self.financial_terms):
            concepts.append('financial')
        
        # Determine context
        if 'mining' in concepts:
            context = 'mining'
        elif 'companies' in concepts:
            context = 'corporate'
        elif 'financial' in concepts:
            context = 'financial'
        else:
            context = 'general'
        
        # Log analysis for debugging
        concepts_str = ','.join(concepts) if concepts else '='
        logger.info(f"Headline analysis: concepts={concepts_str}, context={context}")
        
        return {
            'concepts': concepts,
            'context': context,
            'companies': [],  # Simplified - no complex company extraction
            'financial_amounts': [],  # Simplified - no complex amount extraction
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Basic entity extraction for compatibility"""
        return {
            'companies': [],
            'concepts': [],
            'regulatory': [],
            'financial_amounts': [],
            'technical_specs': []
        }