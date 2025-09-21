"""
Utility functions for Bitcoin Mining News Bot
"""

import json
import logging
import os
import random
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List

from config import BotConstants

logger = logging.getLogger('bitcoin_mining_bot')


class RuntimeLogger:
    """Handles runtime logging for content filtering and blocking"""
    
    @staticmethod
    def ensure_runtime_logs_dir():
        """Ensure the runtime logs directory exists"""
        # Use environment variable if set, otherwise fall back to default locations
        log_dir = os.environ.get("RUNTIME_LOGS_DIR")
        if log_dir:
            try:
                os.makedirs(log_dir, exist_ok=True)
                return log_dir
            except Exception as e:
                logger.warning(f"Could not create runtime logs directory at {log_dir}: {e}")
        
        # Fallback to GitHub Actions runner temp directory if available
        runner_temp = os.environ.get("RUNNER_TEMP")
        if runner_temp:
            log_dir = os.path.join(runner_temp, "runtime-logs")
            try:
                os.makedirs(log_dir, exist_ok=True)
                return log_dir
            except Exception as e:
                logger.warning(f"Could not create runtime logs directory at {log_dir}: {e}")
        
        # Final fallback to temp directory
        log_dir = "/tmp/runtime-logs"
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create runtime logs directory at {log_dir}: {e}")
            # If even /tmp fails, use current directory
            log_dir = "./runtime-logs"
            os.makedirs(log_dir, exist_ok=True)
        return log_dir
    
    @staticmethod
    def log_blocked_content(content_type: str, title: str, reason: str):
        """Log blocked content to the runtime logs"""
        try:
            log_dir = RuntimeLogger.ensure_runtime_logs_dir()
            
            # Log to JSONL file
            jsonl_file = os.path.join(log_dir, "blocked.jsonl")
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "content_type": content_type,
                "title": title,
                "reason": reason
            }
            
            with open(jsonl_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            # Log to markdown file
            md_file = os.path.join(log_dir, "blocked.md")
            if not os.path.exists(md_file):
                with open(md_file, "w") as f:
                    f.write("# Blocked Content Log\n\n")
                    f.write("This file tracks content that was filtered or blocked during bot execution.\n\n")
            
            with open(md_file, "a") as f:
                f.write(f"## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"- **Type**: {content_type}\n")
                f.write(f"- **Title**: {title}\n")
                f.write(f"- **Reason**: {reason}\n\n")
                
        except Exception as e:
            logger.warning(f"Could not write to runtime logs: {e}")
            # Continue execution - logging failure shouldn't break the bot
    
    @staticmethod
    def initialize_runtime_logs():
        """Initialize runtime log files if they don't exist"""
        try:
            log_dir = RuntimeLogger.ensure_runtime_logs_dir()
            
            jsonl_file = os.path.join(log_dir, "blocked.jsonl")
            md_file = os.path.join(log_dir, "blocked.md")
            
            # Create empty JSONL file if it doesn't exist
            if not os.path.exists(jsonl_file):
                with open(jsonl_file, "w") as f:
                    pass  # Create empty file
            
            # Create markdown header if file doesn't exist
            if not os.path.exists(md_file):
                with open(md_file, "w") as f:
                    f.write("# Runtime Logs\n\n")
                    f.write(f"Bot execution started at: {datetime.now().isoformat()}\n\n")
                    f.write("No content was blocked during this run.\n")
                    
        except Exception as e:
            logger.warning(f"Could not initialize runtime logs: {e}")
            # Continue execution - logging initialization failure shouldn't break the bot


class FileManager:
    """Manages file operations for the bot"""
    
    @staticmethod
    def _load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
        """Generic JSON file loader with error handling"""
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    @staticmethod
    def _save_json_file(file_path: str, data: Dict[str, Any]) -> None:
        """Generic JSON file saver"""
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_posted_articles() -> Dict[str, Any]:
        """Load the list of already posted article URIs and queued articles"""
        data = FileManager._load_json_file(BotConstants.POSTED_ARTICLES_FILE)
        if data is None:
            logger.info("No existing posted articles file found, creating new one")
            return {"posted_uris": [], "queued_articles": [], "last_run_time": None}
        
        # Auto-upgrade old format to include queued_articles and last_run_time
        if "queued_articles" not in data:
            data["queued_articles"] = []
            logger.info("Auto-upgrading posted_articles.json to include queued_articles")
        if "last_run_time" not in data:
            data["last_run_time"] = None
            logger.info("Auto-upgrading posted_articles.json to include last_run_time")
        return data
    
    @staticmethod
    def save_posted_articles(posted_articles: Dict[str, Any]) -> None:
        """Save the list of posted article URIs and queued articles"""
        # Update last run time before saving
        posted_articles["last_run_time"] = datetime.now().isoformat()
        
        FileManager._save_json_file(BotConstants.POSTED_ARTICLES_FILE, posted_articles)
        queued_count = len(posted_articles.get("queued_articles", []))
        posted_count = len(posted_articles["posted_uris"])
        logger.info(f"Saved {posted_count} posted article URIs and {queued_count} queued articles")
    
    @staticmethod
    def load_rate_limit_cooldown() -> Optional[Dict[str, Any]]:
        """Load rate limit cooldown data"""
        return FileManager._load_json_file(BotConstants.RATE_LIMIT_COOLDOWN_FILE)
    
    @staticmethod
    def save_rate_limit_cooldown(cooldown_data: Dict[str, Any]) -> None:
        """Save rate limit cooldown data"""
        FileManager._save_json_file(BotConstants.RATE_LIMIT_COOLDOWN_FILE, cooldown_data)
    
    @staticmethod
    def remove_rate_limit_cooldown() -> None:
        """Remove rate limit cooldown file"""
        try:
            os.remove(BotConstants.RATE_LIMIT_COOLDOWN_FILE)
        except FileNotFoundError:
            pass


class TimeUtils:
    """Time-related utility functions"""
    
    @staticmethod
    def is_minimum_interval_respected(last_run_time: Optional[str]) -> bool:
        """Check if at least 90 minutes have passed since the last successful run"""
        if not last_run_time:
            return True  # No previous run recorded
        
        try:
            last_run = datetime.fromisoformat(last_run_time)
            time_since_last_run = datetime.now() - last_run
            minimum_interval = timedelta(minutes=BotConstants.MINIMUM_INTERVAL_MINUTES)
            
            if time_since_last_run < minimum_interval:
                remaining_minutes = int((minimum_interval - time_since_last_run).total_seconds() / 60)
                logger.warning(f"Minimum {BotConstants.MINIMUM_INTERVAL_MINUTES}-minute interval not respected. "
                             f"Last run was {int(time_since_last_run.total_seconds() / 60)} minutes ago. "
                             f"Waiting {remaining_minutes} more minutes.")
                return False
            return True
        except (ValueError, TypeError):
            logger.warning("Invalid last_run_time format, proceeding with run")
            return True
    
    @staticmethod
    def is_rate_limit_cooldown_active(cooldown_data: Optional[Dict[str, Any]]) -> bool:
        """Check if we're still in rate limit cooldown period"""
        if not cooldown_data:
            return False
            
        try:
            cooldown_timestamp = datetime.fromisoformat(cooldown_data["cooldown_until"])
            
            if datetime.now() < cooldown_timestamp:
                remaining_seconds = (cooldown_timestamp - datetime.now()).total_seconds()
                remaining_hours = int(remaining_seconds / 3600)
                remaining_minutes = int((remaining_seconds % 3600) / 60)
                
                if remaining_hours > 0:
                    logger.warning(f"Rate limit cooldown active. Skipping run. {remaining_hours}h {remaining_minutes}m remaining.")
                else:
                    logger.warning(f"Rate limit cooldown active. Skipping run. {remaining_minutes} minutes remaining.")
                return True
            else:
                # Cooldown period has passed
                FileManager.remove_rate_limit_cooldown()
                logger.info("Rate limit cooldown period ended. Proceeding with normal operation.")
                return False
        except (KeyError, ValueError):
            # Invalid format - proceed normally
            return False
    
    @staticmethod
    def create_rate_limit_cooldown() -> Dict[str, Any]:
        """Create a new rate limit cooldown period"""
        # Simple cooldown: Start with 2 hours, then 4 hours for subsequent hits
        existing_cooldown_exists = os.path.exists(BotConstants.RATE_LIMIT_COOLDOWN_FILE)
        cooldown_hours = BotConstants.RATE_LIMIT_SUBSEQUENT_HOURS if existing_cooldown_exists else BotConstants.RATE_LIMIT_INITIAL_HOURS
        
        cooldown_until = datetime.now() + timedelta(hours=cooldown_hours)
        cooldown_data = {
            "cooldown_until": cooldown_until.isoformat(),
            "reason": f"Twitter API rate limit exceeded ({BotConstants.DAILY_REQUEST_LIMIT} requests per 24 hours)",
            "created_at": datetime.now().isoformat(),
            "duration_hours": cooldown_hours
        }
        
        logger.warning(f"Rate limit cooldown set for {cooldown_hours} hours. "
                      f"Bot will not run until: {cooldown_until.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.warning("This prevents the bot from exceeding Twitter's rate limits.")
        
        return cooldown_data


class TextUtils:
    """Text processing utility functions"""
    
    # Abbreviations to save characters
    ABBREVIATIONS = {
        "Bitcoin": "BTC",
        "bitcoin": "BTC", 
        "with": "w/",
        "year": "yr",
        "years": "yrs",
        "million": "M",
        "Million": "M", 
        "billion": "B",
        "Billion": "B",
        "thousand": "K",
        "Thousand": "K",
        "mining": "mining",  # Keep this as is since it's key
        "company": "co",
        "Company": "Co",
        "investment": "invest",
        "Investment": "Invest"
    }
    
    @staticmethod
    def extract_key_info(article: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key information from article for creating informative tweets"""
        from entity_extractor import EntityExtractor
        
        title = article.get("title", "") or ""
        body = article.get("body", "") or ""
        text = f"{title} {body}"
        
        # Initialize entity extractor
        extractor = EntityExtractor()
        entities = extractor.extract_entities(title)
        
        # Enhanced company detection patterns - improved to avoid false positives
        companies = list(entities.get("companies", []))
        
        # Look for additional company patterns in the text
        company_patterns = [
            r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(?:Holdings?|Corporation|Corp|Inc|LLC|Ltd|Co\.?)\b',  # Corporate entities
            r'\b(CleanSpark|Marathon Digital|Riot Platforms|MicroStrategy|Tesla|Core Scientific|Hive Blockchain|Bitfarms|Argo Blockchain|Hut 8|Canaan|Bitmain|IREN)\b',  # Known mining companies
            r'\b([A-Z][a-zA-Z]+)\s+(?:Holdings?)\b',  # "DL Holdings", "ABC Holding"
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean up the match and avoid nonsensical extractions
                if match and len(match) > 2 and match.lower() not in [c.lower() for c in companies]:
                    # Don't add if it contains words that suggest it's not a real company
                    if not any(word in match.lower() for word in ['stole', 'steal', 'boss', 'chief', 'head', 'arrest', 'charge', 'million', 'investment']):
                        companies.append(match)
        
        # Extract financial amounts (dollars, BTC amounts)
        financial_amounts = []
        amount_patterns = [
            r'\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|M|B))?',  # $1.5M, $21.85M
            r'[\d,]+\s*BTC',  # 200 BTC
            r'[\d,]+\s*Bitcoin',  # 200 Bitcoin
            r'[\d,]+\s*(?:million|billion)\s*(?:dollars?)?',  # 21.85 million dollars
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            financial_amounts.extend(matches)
        
        # Extract numbers and technical specs
        technical_specs = []
        tech_patterns = [
            r'[\d,]+\+?\s*(?:miners?|rigs?)',  # 2,200+ miners
            r'[\d,]+\s*(?:MW|GW|TH/s|EH/s)',  # power/hashrate specs
            r'[\d,]+\s*(?:annually|per year|/yr)',  # annual targets
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            technical_specs.extend(matches)
        
        return {
            "companies": companies,
            "locations": entities.get("locations", []),
            "regulatory": entities.get("regulatory", []),
            "financial_amounts": financial_amounts,
            "technical_specs": technical_specs,
            "concepts": entities.get("concepts", [])
        }
    
    @staticmethod
    def create_enhanced_tweet_text(article: Dict[str, Any]) -> str:
        """Create informative, concise tweet text prioritizing key details"""
        try:
            # Prefer Gemini-generated headline over original title
            gemini_headline = article.get("gemini_headline", "")
            original_title = article.get("title", "")
            
            # Use Gemini headline if it's meaningful, otherwise fall back to original title
            if gemini_headline and gemini_headline.strip():
                title = gemini_headline
            else:
                title = original_title
            
            if not title or not title.strip():
                return TextUtils.create_original_tweet_text(article)  # fallback to original
            
            # Extract key information
            info = TextUtils.extract_key_info(article)
            
            # Determine the primary structure based on content
            title_lower = title.lower()
            
            # Check for negative news that shouldn't use company investment format
            negative_keywords = ['stole', 'steal', 'theft', 'arrest', 'charge', 'scandal', 'illegal', 'fraud', 'crime']
            is_negative_news = any(word in title_lower for word in negative_keywords)
            
            # Strategy 1: Company-focused format (only for positive business news)
            if not is_negative_news and info["companies"] and info["financial_amounts"]:
                # Further check that it's actually about business investments
                business_keywords = ['invest', 'expand', 'launch', 'partner', 'acquire', 'announce', 'facility', 'operation']
                if any(word in title_lower for word in business_keywords):
                    return TextUtils._create_company_focused_tweet(info, title, title_lower)
            
            # Strategy 2: News-focused format for regulatory/general news
            if info["regulatory"] or any(word in title_lower for word in ["approve", "regulation", "legal"]):
                return TextUtils._create_news_focused_tweet(info, title)
            
            # Strategy 3: Enhanced generic format (fallback for all other cases)
            return TextUtils._create_enhanced_generic_tweet(info, title)
            
        except Exception as e:
            logger.error(f"Error creating enhanced tweet text: {str(e)}")
            # Fallback to original method
            return TextUtils.create_original_tweet_text(article)
    
    @staticmethod
    def _create_company_focused_tweet(info: Dict[str, Any], title: str, title_lower: str) -> str:
        """Create company-focused tweet format: 'Company invests $X in BTC mining via Partner. Target: Y'"""
        
        # Check if this is actually about company investments/business actions
        # If it's about crime, scandal, or negative news, fall back to generic format
        negative_keywords = ['stole', 'steal', 'theft', 'arrest', 'charge', 'scandal', 'illegal', 'fraud', 'crime']
        if any(word in title_lower for word in negative_keywords):
            return TextUtils._create_enhanced_generic_tweet(info, title)
        
        # Only proceed with company format if we have legitimate companies
        if not info["companies"] or len(info["companies"]) < 1:
            return TextUtils._create_enhanced_generic_tweet(info, title)
            
        components = []
        
        # Primary company
        primary_company = info["companies"][0]
        components.append(primary_company)
        
        # Action verb
        action = "invests"
        if any(word in title_lower for word in ["expand", "expansion"]):
            action = "expands"
        elif any(word in title_lower for word in ["launch", "start"]):
            action = "launches"
        elif any(word in title_lower for word in ["partner", "partnership"]):
            action = "partners w/"
        elif any(word in title_lower for word in ["acquire", "acquisition"]):
            action = "acquires"
        
        components.append(action)
        
        # Financial amount (prioritize dollar amounts)
        financial_detail = ""
        if info["financial_amounts"]:
            dollar_amounts = [a for a in info["financial_amounts"] if '$' in a]
            if dollar_amounts:
                financial_detail = dollar_amounts[0]
            else:
                financial_detail = info["financial_amounts"][0]
            components.append(financial_detail)
        
        components.append("in BTC mining")
        
        # Partner company
        if len(info["companies"]) > 1:
            components.append(f"via {info['companies'][1]}")
        
        # Technical specs as target
        if info["technical_specs"]:
            # Add period and start new sentence for technical details
            base_text = " ".join(components) + "."
            tech_detail = info["technical_specs"][0]
            if "annually" in tech_detail or "/yr" in tech_detail or "per year" in tech_detail:
                full_text = f"{base_text} Target: {tech_detail}"
            else:
                full_text = f"{base_text} Specs: {tech_detail}"
            
            # Apply abbreviations and check length
            full_text = TextUtils._apply_abbreviations(full_text)
            if len(full_text) <= BotConstants.TWEET_MAX_LENGTH:
                return full_text
        
        # If tech specs make it too long, return base without tech details
        base_text = " ".join(components)
        return TextUtils._apply_abbreviations(base_text)
    
    @staticmethod
    def _create_news_focused_tweet(info: Dict[str, Any], title: str) -> str:
        """Create news-focused format for regulatory/general news"""
        # For regulatory news, keep the authoritative structure but enhance with abbreviations
        enhanced_title = title
        
        # Add financial context if available and not already in title
        if info["financial_amounts"] and not any(amt.replace('$', '').replace(',', '') in title for amt in info["financial_amounts"]):
            amount = info["financial_amounts"][0]
            enhanced_title = f"{amount}: {enhanced_title}"
        
        # Apply abbreviations
        enhanced_title = TextUtils._apply_abbreviations(enhanced_title)
        
        # Ensure length compliance
        if len(enhanced_title) > BotConstants.TWEET_MAX_LENGTH:
            enhanced_title = enhanced_title[:BotConstants.TWEET_TRUNCATE_LENGTH] + "..."
        
        return enhanced_title
    
    @staticmethod
    def _create_enhanced_generic_tweet(info: Dict[str, Any], title: str) -> str:
        """Create enhanced generic format"""
        components = []
        
        # Add location if available and significant
        if info["locations"]:
            location = info["locations"][0].title()
            if location.lower() not in title.lower():
                components.append(f"{location}:")
        
        # Add financial amount if available and not in title
        if info["financial_amounts"]:
            amount = info["financial_amounts"][0]
            if not any(amt.replace('$', '').replace(',', '') in title for amt in info["financial_amounts"]):
                components.append(f"{amount}:")
        
        # Add the title
        components.append(title)
        
        # Combine and apply abbreviations
        tweet_text = " ".join(components)
        tweet_text = TextUtils._apply_abbreviations(tweet_text)
        
        # Ensure length compliance
        if len(tweet_text) > BotConstants.TWEET_MAX_LENGTH:
            tweet_text = tweet_text[:BotConstants.TWEET_TRUNCATE_LENGTH] + "..."
        
        return tweet_text
    
    @staticmethod
    def _enhance_generic_title(title: str, info: Dict[str, Any]) -> str:
        """Enhance a generic title with extracted information"""
        # Remove common prefixes that don't add value
        title = re.sub(r'^(Breaking|News|Update|Alert):\s*', '', title, flags=re.IGNORECASE)
        
        # If we have financial info, try to incorporate it
        if info["financial_amounts"]:
            amount = info["financial_amounts"][0]
            if amount not in title:
                title = f"{amount}: {title}"
        
        # Add location if significant and not already mentioned
        if info["locations"] and info["locations"][0] not in title:
            location = info["locations"][0]
            title = f"{location}: {title}"
        
        return title
    
    @staticmethod
    def _apply_abbreviations(text: str) -> str:
        """Apply abbreviations to save characters"""
        for full_word, abbrev in TextUtils.ABBREVIATIONS.items():
            # Use word boundaries to avoid partial replacements
            text = re.sub(r'\b' + re.escape(full_word) + r'\b', abbrev, text)
        return text

    @staticmethod
    def create_hook_tweet(article: Dict[str, Any]) -> str:
        """Create the hook/benefit tweet that leads the thread."""
        return TextUtils.create_enhanced_tweet_text(article)

    @staticmethod
    def create_link_tweet(article: Dict[str, Any]) -> str:
        """Create the succinct link tweet with a call-to-action."""
        url = (article.get("url") or article.get("uri") or "").strip()
        if not url:
            return ""

        call_to_action = getattr(BotConstants, "TWEET_CALL_TO_ACTION", "Read more:").strip()
        if call_to_action:
            link_tweet = f"{call_to_action} {url}".strip()
        else:
            link_tweet = url

        if len(link_tweet) > BotConstants.TWEET_MAX_LENGTH:
            if len(url) <= BotConstants.TWEET_MAX_LENGTH:
                return url[:BotConstants.TWEET_MAX_LENGTH]
            return url[:BotConstants.TWEET_TRUNCATE_LENGTH] + "..."

        return link_tweet

    @staticmethod
    def create_thread_texts(article: Dict[str, Any]) -> Tuple[str, str]:
        """Return both tweets for a two-part thread."""
        hook_tweet = TextUtils.create_hook_tweet(article)
        
        # Check if hook tweet already contains a URL
        article_url = (article.get("url") or article.get("uri") or "").strip()
        if article_url and article_url in hook_tweet:
            # If hook tweet already has the URL, create a link tweet without the URL
            call_to_action = getattr(BotConstants, "TWEET_CALL_TO_ACTION", "Read more:").strip()
            link_tweet = call_to_action if call_to_action else ""
        else:
            # Normal case: create link tweet with URL
            link_tweet = TextUtils.create_link_tweet(article)
        
        return hook_tweet, link_tweet

    @staticmethod
    def create_tweet_text(article: Dict[str, Any]) -> str:
        """Create catchy tweet text for the article (enhanced version)"""
        # Use the enhanced method by default
        return TextUtils.create_hook_tweet(article)
    
    @staticmethod
    def create_original_tweet_text(article: Dict[str, Any]) -> str:
        """Original tweet text creation method (kept for fallback)"""
        try:
            # Choose a catchy prefix
            prefix = random.choice(BotConstants.TWEET_PREFIXES)

            # Create a summary (use Gemini headline if available and meaningful, otherwise article title)
            gemini_headline = article.get("gemini_headline", "")
            original_title = article.get("title", "")
            
            # Use Gemini headline if it's meaningful, otherwise fall back to original title
            if gemini_headline and gemini_headline.strip():
                title = gemini_headline
            else:
                title = original_title or ""
                
            title = title.strip() if title else ""

            # Clean up and shorten the title if needed
            if len(title) <= BotConstants.TITLE_MAX_LENGTH:  # Leave some room for the prefix
                summary = title
            else:
                # Take first sentence or truncate
                first_period = title.find(".")
                if first_period > 0 and first_period < BotConstants.TITLE_MAX_LENGTH:
                    summary = title[:first_period+1]
                else:
                    summary = title[:BotConstants.TITLE_MAX_LENGTH] + "..."

            # Create the tweet text with the prefix
            tweet_text = f"{prefix}{summary}"

            # Truncate if too long for Twitter (280 character limit)
            if len(tweet_text) > BotConstants.TWEET_MAX_LENGTH:
                tweet_text = tweet_text[:BotConstants.TWEET_TRUNCATE_LENGTH] + "..."

            return tweet_text

        except Exception as e:
            logger.error(f"Error creating tweet text: {str(e)}")
            # Return a fallback tweet text with proper None handling
            gemini_headline = article.get("gemini_headline", "")
            original_title = article.get("title", "")
            fallback_title = gemini_headline if gemini_headline and gemini_headline.strip() else original_title or ""
            return "New Bitcoin mining article: " + fallback_title[:BotConstants.TITLE_MAX_LENGTH]