"""
Entity Extraction for Bitcoin Mining News Bot
--------------------------------------------
This module extracts relevant entities from news headlines for image selection.
"""

import re
import logging
from typing import List, Dict, Set, Tuple

logger = logging.getLogger('entity_extractor')

class EntityExtractor:
    """Extracts entities from Bitcoin news headlines for image selection"""
    
    def __init__(self):
        # US States (commonly mentioned in Bitcoin news)
        self.us_states = {
            'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado',
            'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho',
            'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana',
            'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota',
            'mississippi', 'missouri', 'montana', 'nebraska', 'nevada',
            'new hampshire', 'new jersey', 'new mexico', 'new york',
            'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon',
            'pennsylvania', 'rhode island', 'south carolina', 'south dakota',
            'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington',
            'west virginia', 'wisconsin', 'wyoming'
        }
        
        # Countries commonly mentioned in Bitcoin news
        self.countries = {
            'united states', 'usa', 'america', 'china', 'japan', 'south korea',
            'singapore', 'hong kong', 'taiwan', 'india', 'thailand', 'philippines',
            'indonesia', 'vietnam', 'malaysia', 'australia', 'new zealand',
            'canada', 'mexico', 'brazil', 'argentina', 'chile', 'colombia',
            'venezuela', 'united kingdom', 'uk', 'england', 'scotland', 'wales',
            'ireland', 'france', 'germany', 'italy', 'spain', 'portugal',
            'netherlands', 'belgium', 'switzerland', 'austria', 'sweden',
            'norway', 'denmark', 'finland', 'poland', 'russia', 'ukraine',
            'turkey', 'israel', 'uae', 'saudi arabia', 'nigeria', 'south africa',
            'kenya', 'egypt'
        }
        
        # Crypto companies commonly mentioned
        self.crypto_companies = {
            'coinbase', 'binance', 'kraken', 'bitstamp', 'gemini', 'bitfinex',
            'microstrategy', 'tesla', 'square', 'paypal', 'marathon digital',
            'riot blockchain', 'core scientific', 'hive blockchain',
            'bitfarms', 'argo blockchain', 'hut 8', 'canaan', 'bitmain',
            'nvidia', 'amd', 'intel'
        }
        
        # Regulatory agencies and bodies
        self.regulatory_bodies = {
            'sec', 'securities and exchange commission', 'cftc',
            'commodity futures trading commission', 'irs', 'internal revenue service',
            'treasury', 'fed', 'federal reserve', 'fdic', 'occ',
            'fincen', 'treasury department', 'department of treasury',
            'congress', 'senate', 'house of representatives', 'white house'
        }
        
        # Bitcoin-related concepts that suggest specific imagery
        self.bitcoin_concepts = {
            'mining': 'mining_equipment',
            'hashrate': 'mining_chart',
            'difficulty': 'mining_chart', 
            'halving': 'bitcoin_chart',
            'price': 'price_chart',
            'etf': 'financial_chart',
            'adoption': 'adoption_concept',
            'regulation': 'regulatory_concept',
            'ban': 'regulatory_concept',
            'legal': 'regulatory_concept',
            'law': 'regulatory_concept',
            'bill': 'regulatory_concept',
            'reserve': 'treasury_concept'
        }
    
    def extract_entities(self, headline: str) -> Dict[str, List[str]]:
        """Extract all relevant entities from a headline"""
        if not headline:
            return {
                'locations': [],
                'companies': [],
                'regulatory': [],
                'concepts': []
            }
        
        headline_lower = headline.lower()
        
        entities = {
            'locations': [],
            'companies': [],
            'regulatory': [],
            'concepts': []
        }
        
        # Extract US states
        for state in self.us_states:
            if self._find_entity_in_text(state, headline_lower):
                entities['locations'].append(state)
        
        # Extract countries
        for country in self.countries:
            if self._find_entity_in_text(country, headline_lower):
                entities['locations'].append(country)
        
        # Extract companies
        for company in self.crypto_companies:
            if self._find_entity_in_text(company, headline_lower):
                entities['companies'].append(company)
        
        # Extract regulatory bodies
        for body in self.regulatory_bodies:
            if self._find_entity_in_text(body, headline_lower):
                entities['regulatory'].append(body)
        
        # Extract concepts
        for concept, image_type in self.bitcoin_concepts.items():
            if self._find_entity_in_text(concept, headline_lower):
                entities['concepts'].append(concept)
        
        return entities
    
    def _find_entity_in_text(self, entity: str, text: str) -> bool:
        """Find entity in text using word boundaries to avoid false positives"""
        # Use word boundaries for better matching
        pattern = r'\b' + re.escape(entity) + r'\b'
        return bool(re.search(pattern, text, re.IGNORECASE))
    
    def get_primary_entity(self, entities: Dict[str, List[str]]) -> Tuple[str, str]:
        """Get the most relevant entity for image selection"""
        # Priority order: locations > companies > regulatory > concepts
        
        if entities['locations']:
            # Prefer US states over countries for specificity
            for location in entities['locations']:
                if location in self.us_states:
                    return ('locations', location)
            # If no US states, return first country
            return ('locations', entities['locations'][0])
        
        if entities['companies']:
            return ('companies', entities['companies'][0])
        
        if entities['regulatory']:
            return ('regulatory', entities['regulatory'][0])
        
        if entities['concepts']:
            return ('concepts', entities['concepts'][0])
        
        return ('', '')
    
    def get_bitcoin_context(self, headline: str) -> str:
        """Determine the Bitcoin context for selecting appropriate Bitcoin imagery"""
        headline_lower = headline.lower()
        
        # ETF context (highest priority for regulatory approval)
        if any(term in headline_lower for term in ['etf', 'fund', 'investment']):
            return 'etf'
        
        # Regulatory context (high priority)
        if any(term in headline_lower for term in ['regulation', 'legal', 'law', 'ban', 'approve']):
            return 'regulatory'
        
        # Mining-related context
        if any(term in headline_lower for term in ['mining', 'miner', 'hashrate', 'difficulty']):
            return 'mining'
        
        # Price/financial context
        if any(term in headline_lower for term in ['price', 'value', 'worth', 'cost', 'expensive']):
            return 'price'
        
        # Adoption context
        if any(term in headline_lower for term in ['adoption', 'accept', 'payment', 'reserve']):
            return 'adoption'
        
        # Default to general Bitcoin
        return 'general'
    
    def analyze_headline(self, headline: str) -> Dict:
        """Complete analysis of headline for image selection"""
        entities = self.extract_entities(headline)
        primary_entity_type, primary_entity = self.get_primary_entity(entities)
        bitcoin_context = self.get_bitcoin_context(headline)
        
        analysis = {
            'headline': headline,
            'entities': entities,
            'primary_entity': {
                'type': primary_entity_type,
                'value': primary_entity
            },
            'bitcoin_context': bitcoin_context,
            'has_specific_entity': bool(primary_entity_type)
        }
        
        logger.info(f"Headline analysis: {primary_entity_type}={primary_entity}, context={bitcoin_context}")
        return analysis