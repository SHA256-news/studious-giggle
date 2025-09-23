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


class FormattingUtils:
    """Common formatting utilities to reduce code duplication"""
    
    @staticmethod
    def format_article_title(article: Dict[str, Any], max_length: int = 50, add_ellipsis: bool = True) -> str:
        """Format article title with consistent truncation logic
        
        Args:
            article: Article dictionary that may contain 'title' or 'gemini_headline'
            max_length: Maximum length before truncation
            add_ellipsis: Whether to add '...' after truncation
        
        Returns:
            Formatted title string
        """
        # Try gemini_headline first, then title, then fallback
        title = article.get("gemini_headline") or article.get("title", "Unknown title")
        
        if len(title) <= max_length:
            return title + ("..." if add_ellipsis else "")
        else:
            return title[:max_length] + ("..." if add_ellipsis else "")
    
    @staticmethod 
    def get_queue_count_message(queued_articles: List[Dict[str, Any]]) -> str:
        """Generate consistent queue count message"""
        queue_count = len(queued_articles)
        return f", {queue_count} total in queue" if queue_count > 0 else ""
    
    @staticmethod
    def format_execution_time_message(execution_time: float, status: str) -> str:
        """Format consistent execution time logging"""
        return f"⏱️  Total execution time: {execution_time:.2f} seconds"


class ErrorHandlingUtils:
    """Centralized error handling utilities"""
    
    @staticmethod
    def log_missing_api_keys_error():
        """Log the standard missing API keys error message"""
        logger.error("🚨 CONFIGURATION ERROR: Missing required environment variables")
        logger.error("This error occurs when the bot cannot find the required API keys.")
        logger.error("")
        logger.error("To fix this issue:")
        logger.error("1. Go to your GitHub repository settings")
        logger.error("2. Navigate to Settings > Secrets and variables > Actions")
        logger.error("3. Add the following repository secrets:")
        for var in ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", 
                   "TWITTER_ACCESS_TOKEN_SECRET", "EVENTREGISTRY_API_KEY"]:
            logger.error(f"   • {var}")
        logger.error("")
        logger.error("For detailed setup instructions, see the README.md file.")
    
    @staticmethod
    def log_comprehensive_api_key_diagnosis(queued_count: int):
        """Show comprehensive diagnosis for missing API keys (GitHub Actions context)"""
        logger.error("="*80)
        logger.error("🔍 DIAGNOSIS: GitHub Action 'Success' but No Tweets Posted")
        logger.error("="*80)
        logger.error("")
        logger.error("✅ WHAT WORKED:")
        logger.error("   - Dependencies installed successfully")
        logger.error("   - Bot code executed without errors")
        logger.error("   - Python imports and initialization completed")
        logger.error("   - Error handling worked correctly")
        logger.error("")
        logger.error("❌ WHAT FAILED:")
        logger.error("   - Missing required API credentials")
        logger.error("   - Unable to connect to Twitter API")
        logger.error("   - Unable to connect to EventRegistry API")
        logger.error("   - Cannot post tweets without valid authentication")
        logger.error("")
        if queued_count > 0:
            logger.error(f"📋 ARTICLES WAITING: {queued_count} articles are queued for posting")
            logger.error("   These articles will be posted automatically once API keys are configured.")
            logger.error("")
        logger.error("🔧 SOLUTION: Configure GitHub Repository Secrets")
        logger.error("   1. Go to your repository Settings > Secrets and variables > Actions")
        logger.error("   2. Add these repository secrets:")
        for var in ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", 
                   "TWITTER_ACCESS_TOKEN_SECRET", "EVENTREGISTRY_API_KEY"]:
            logger.error(f"      - {var}")
        logger.error("")
        logger.error("💡 WHY GITHUB ACTIONS SHOW 'SUCCESS':")
        logger.error("   - The workflow completes all steps without exceptions")
        logger.error("   - Dependencies install successfully")
        logger.error("   - The bot gracefully handles missing credentials")
        logger.error("   - No Python errors or crashes occur")
        logger.error("   - 'Success' means the code ran, not that tweets were posted")
        logger.error("")
        logger.error("📖 For API key setup guides:")
        logger.error("   - Twitter: https://developer.twitter.com/")
        logger.error("   - EventRegistry: https://newsapi.ai/dashboard")
        logger.error("")
        logger.error("🔍 Run diagnostics: python bot.py --diagnose")
        logger.error("="*80)
    
    @staticmethod
    def log_execution_status(execution_time: float, status: str, success: bool = True):
        """Log consistent execution status"""
        time_msg = FormattingUtils.format_execution_time_message(execution_time, status)
        status_symbol = "✅" if success else "❌"
        logger.info(f"{time_msg}")
        logger.info(f"{status_symbol} Status: {status}")


class QueueUtils:
    """Utilities for queue management to reduce repetitive patterns"""
    
    @staticmethod
    def get_queued_articles(posted_articles: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get queued articles with consistent access pattern"""
        return posted_articles.get("queued_articles", [])
    
    @staticmethod
    def set_queued_articles(posted_articles: Dict[str, Any], articles: List[Dict[str, Any]]) -> None:
        """Set queued articles with consistent pattern"""
        posted_articles.setdefault("queued_articles", []).clear()
        posted_articles["queued_articles"].extend(articles)


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
        
        # For GitHub Actions, use the current directory's runtime-logs folder
        # This matches where the workflow creates and expects to find the files
        if os.environ.get("GITHUB_ACTIONS"):
            log_dir = "./runtime-logs"
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
    def save_posted_articles(posted_articles: Dict[str, Any], update_last_run_time: bool = False) -> None:
        """Save the list of posted article URIs and queued articles
        
        Args:
            posted_articles: The data to save
            update_last_run_time: Whether to update the last_run_time (only on successful bot completion)
        """
        # Only update last run time if explicitly requested
        if update_last_run_time:
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


class TextPatterns:
    """Centralized text patterns for consistent text processing"""
    
    FINANCIAL_PATTERNS = [
        r'\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|m|b))?',
        r'[\d,]+\s*(?:million|billion)',
        r'[\d,]+\s*btc',
        r'[\d,]+\s*bitcoin'
    ]
    
    COMPANY_PATTERNS = [
        r'\b(cleanspark|marathon|riot|microstrategy|tesla|coinbase|binance|bitfarms|hive|core\s*scientific)\b',
    ]
    
    TECH_PATTERNS = [
        r'[\d,]+\s*(?:eh/s|th/s|mw|gw)',
        r'[\d,]+\s*(?:miners?|rigs?)',
        r'[\d,]+\s*(?:annually|per\s*year)'
    ]
    
    KEY_TERMS = ['credit', 'line', 'investment', 'facility', 'partnership', 'expansion', 'mining', 'bitcoin', 'btc']
    
    TRAILING_WORDS = ["at", "from", "on", "in", "via", "to", "by"]


class ContentFilter:
    """Handles filtering of repetitive content in tweets"""
    
    @staticmethod
    def filter_repetitive_content(summary: str, hook_tweet: str, article: Dict[str, Any]) -> str:
        """Filter out content from summary that's already mentioned in hook tweet"""
        if not summary or not hook_tweet:
            return summary
            
        summary_lines = ContentFilter._split_summary_lines(summary)
        if not summary_lines:
            return summary
            
        hook_keywords, hook_tech_specs = ContentFilter._extract_hook_keywords(hook_tweet)
        filtered_lines = ContentFilter._filter_summary_lines(summary_lines, hook_keywords, hook_tech_specs)
        
        return '\n'.join(filtered_lines) if filtered_lines else TextUtils._extract_unique_summary_info(article, hook_tweet)

    @staticmethod
    def _split_summary_lines(summary: str) -> List[str]:
        """Split summary into clean lines"""
        return [line.strip() for line in summary.split('\n') if line.strip()]

    @staticmethod
    def _extract_hook_keywords(hook_tweet: str) -> Tuple[set, set]:
        """Extract keywords and technical specs from hook tweet"""
        hook_lower = hook_tweet.lower()
        hook_keywords = set()
        
        # Extract financial amounts with better normalization
        for pattern in TextPatterns.FINANCIAL_PATTERNS:
            matches = re.findall(pattern, hook_lower)
            for match in matches:
                # Normalize financial amounts to handle M/million equivalence
                normalized = ContentFilter._normalize_financial_amount(match)
                if normalized:
                    hook_keywords.add(normalized)
                    # Also add the original form
                    hook_keywords.add(match.replace('$', '').replace(',', '').replace(' ', '').lower())
        
        # Extract company names
        for pattern in TextPatterns.COMPANY_PATTERNS:
            matches = re.findall(pattern, hook_lower)
            hook_keywords.update(matches)
        
        # Extract key terms
        hook_keywords.update(term for term in TextPatterns.KEY_TERMS if term in hook_lower)
        
        # Extract technical specifications
        hook_tech_specs = set()
        for pattern in TextPatterns.TECH_PATTERNS:
            matches = re.findall(pattern, hook_lower)
            for match in matches:
                normalized = re.sub(r'\s+', ' ', match.strip().lower())
                hook_tech_specs.add(normalized)
        
        return hook_keywords, hook_tech_specs

    @staticmethod
    def _filter_summary_lines(summary_lines: List[str], hook_keywords: set, hook_tech_specs: set) -> List[str]:
        """Filter summary lines to remove repetitive content"""
        filtered_lines = []
        
        for line in summary_lines:
            line_lower = line.lower()
            is_repetitive = False
            
            # Check for financial amount repetition
            if ContentFilter._has_repetitive_financial_amounts(line_lower, hook_keywords):
                filtered_line = ContentFilter._remove_financial_amounts_if_additional_content(line, line_lower)
                if filtered_line:
                    # Check if the remaining content after removing financial amounts is still repetitive
                    remaining_lower = filtered_line.lower()
                    if ContentFilter._has_repetitive_key_terms(remaining_lower, hook_keywords):
                        # Skip this line entirely if it's still repetitive
                        is_repetitive = True
                    else:
                        filtered_line = re.sub(r'^[▪•-]\s*', '▪ ', filtered_line)
                        if len(filtered_line) > BotConstants.MIN_MEANINGFUL_CONTENT_LENGTH:
                            filtered_lines.append(filtered_line)
                        is_repetitive = True  # Mark as processed
                else:
                    is_repetitive = True  # Skip if no content remains after removing financial amounts
            
            # Check for company name repetition
            if not is_repetitive:
                for pattern in TextPatterns.COMPANY_PATTERNS:
                    if re.search(pattern, line_lower) and any(company in hook_keywords for company in re.findall(pattern, line_lower)):
                        is_repetitive = True
                        break
            
            # Check for key terms repetition (more aggressive)
            if not is_repetitive and ContentFilter._has_repetitive_key_terms(line_lower, hook_keywords):
                is_repetitive = True
            
            # If line is not repetitive, keep it
            if not is_repetitive:
                filtered_lines.append(line)
        
        return filtered_lines

    @staticmethod
    def _has_repetitive_financial_amounts(line_lower: str, hook_keywords: set) -> bool:
        """Check if line contains financial amounts already in hook"""
        line_amounts = []
        for pattern in TextPatterns.FINANCIAL_PATTERNS:
            matches = re.findall(pattern, line_lower)
            for match in matches:
                # Normalize financial amounts to handle M/million equivalence
                normalized = ContentFilter._normalize_financial_amount(match)
                if normalized:
                    line_amounts.append(normalized)
                # Also add the original form
                line_amounts.append(match.replace('$', '').replace(',', '').replace(' ', '').lower())
        
        return line_amounts and any(amount in hook_keywords for amount in line_amounts)

    @staticmethod
    def _has_repetitive_key_terms(line_lower: str, hook_keywords: set) -> bool:
        """Check if line contains key terms already prominently mentioned in hook"""
        # Count how many key terms overlap
        overlapping_terms = []
        for term in TextPatterns.KEY_TERMS:
            if term in line_lower and term in hook_keywords:
                overlapping_terms.append(term)
        
        # If multiple key terms overlap, consider it repetitive
        # This is more aggressive filtering to avoid content repetition
        if len(overlapping_terms) >= 2:
            return True
        
        # Additional check: if line contains both a company name and a financial term, it's likely repetitive
        has_company = any(company in line_lower for company in ['cleanspark', 'coinbase', 'marathon', 'riot'])
        has_financial_term = any(term in line_lower for term in ['credit', 'line', 'investment', 'facility'])
        
        if has_company and has_financial_term and any(company in hook_keywords for company in ['cleanspark', 'coinbase', 'marathon', 'riot']):
            return True
        
        return False

    @staticmethod
    def _remove_financial_amounts_if_additional_content(line: str, line_lower: str) -> Optional[str]:
        """Remove financial amounts from line if it has additional meaningful content"""
        line_without_amounts = line_lower
        for pattern in TextPatterns.FINANCIAL_PATTERNS:
            line_without_amounts = re.sub(pattern, '', line_without_amounts)
        
        line_words = [w for w in line_without_amounts.split() if len(w) > BotConstants.MIN_WORD_LENGTH]
        if len(line_words) >= BotConstants.MIN_ADDITIONAL_WORDS:  # Has additional meaningful content
            filtered_line = line
            for pattern in TextPatterns.FINANCIAL_PATTERNS:
                filtered_line = re.sub(pattern, '', filtered_line, flags=re.IGNORECASE)
            filtered_line = re.sub(r'\s+', ' ', filtered_line).strip()
            return filtered_line if len(filtered_line) > BotConstants.MIN_FILTERED_LINE_LENGTH else None
        return None

    @staticmethod
    def _normalize_financial_amount(amount_str: str) -> Optional[str]:
        """Normalize financial amounts to handle M/million, B/billion equivalence"""
        if not amount_str:
            return None
            
        # Clean up the amount string
        amount_lower = amount_str.lower().replace('$', '').replace(',', '').strip()
        
        # Extract the number and suffix
        import re
        match = re.match(r'^(\d+(?:\.\d+)?)\s*(m|million|b|billion)?$', amount_lower)
        if not match:
            return None
            
        number = match.group(1)
        suffix = match.group(2) or ''
        
        # Normalize the suffix
        if suffix in ['m', 'million']:
            normalized_suffix = 'million'
        elif suffix in ['b', 'billion']:
            normalized_suffix = 'billion'
        else:
            normalized_suffix = ''
        
        # Return normalized form
        if normalized_suffix:
            return f"{number}{normalized_suffix}"
        else:
            return number


class TweetFormatter:
    """Handles tweet text formatting and enhancement"""
    
    @staticmethod
    def create_enhanced_tweet_text(article: Dict[str, Any]) -> str:
        """Create enhanced tweet text using Gemini headline or fallback formatting"""
        if article is None:
            logger.warning("Received None article in create_enhanced_tweet_text, using fallback")
            return "Bitcoin mining news update"
        
        # If we have Gemini-generated content, use it with minimal enhancement
        gemini_headline = article.get("gemini_headline", "") or ""
        
        if gemini_headline and gemini_headline.strip():
            enhanced_gemini = TweetFormatter._enhance_gemini_headline(gemini_headline, article)
            if len(enhanced_gemini) <= BotConstants.TWEET_MAX_LENGTH:
                return enhanced_gemini
        
        # Fallback to enhanced title processing
        return TweetFormatter._create_enhanced_generic_tweet(article)

    @staticmethod
    def _enhance_gemini_headline(gemini_headline: str, article: Dict[str, Any]) -> str:
        """Enhance a Gemini-generated headline with minimal formatting"""
        if not gemini_headline:
            return ""
            
        enhanced_headline = gemini_headline.strip()
        
        # Add emoji prefix if not already present
        if not any(char in enhanced_headline[:5] for char in ["⚡", "💰", "📈", "🏭", "🎯"]):
            prefix = random.choice(BotConstants.TWEET_PREFIXES)
            enhanced_headline = f"{prefix}{enhanced_headline}"
        
        # Ensure proper sentence case and punctuation
        if enhanced_headline and not enhanced_headline[len(enhanced_headline.split()[0]):].strip().startswith(enhanced_headline.split()[0]):
            if enhanced_headline[-1] not in ".!?":
                enhanced_headline += "..."
        
        return enhanced_headline[:BotConstants.TWEET_MAX_LENGTH]

    @staticmethod
    def _create_enhanced_generic_tweet(article: Dict[str, Any]) -> str:
        """Create enhanced tweet using article info when Gemini content is not available"""
        # Extract key information for intelligent formatting
        info = TextUtils.extract_key_info(article)
        
        # Choose formatting strategy based on content
        if info.get("companies"):
            return TweetFormatter._create_company_focused_tweet(article, info)
        elif info.get("financial_amounts") or info.get("technical_specs"):
            return TweetFormatter._create_news_focused_tweet(article, info)
        else:
            return TweetFormatter._create_basic_tweet(article)

    @staticmethod
    def _create_company_focused_tweet(article: Dict[str, Any], info: Dict[str, Any]) -> str:
        """Create company-focused tweet format"""
        title = (article.get("title") or "").strip()
        companies = info.get("companies", [])
        financial_amounts = info.get("financial_amounts", [])
        
        if not title:
            return "Bitcoin mining news update"
        
        # Use the first company as focus
        main_company = companies[0] if companies else ""
        
        # Create enhanced title with company focus
        if main_company and main_company.lower() not in title.lower():
            # Company not in title, add it
            if financial_amounts:
                enhanced_title = f"{main_company} {financial_amounts[0]} {title}"
            else:
                enhanced_title = f"{main_company}: {title}"
        else:
            enhanced_title = title
        
        # Add emoji and ensure length compliance
        prefix = random.choice(BotConstants.TWEET_PREFIXES)
        
        # Calculate available space for title
        max_title_length = BotConstants.TWEET_MAX_LENGTH - len(prefix)
        
        if len(enhanced_title) > max_title_length:
            enhanced_title = enhanced_title[:max_title_length - 3] + "..."
        
        return f"{prefix}{enhanced_title}"

    @staticmethod
    def _create_news_focused_tweet(article: Dict[str, Any], info: Dict[str, Any]) -> str:
        """Create news-focused tweet with financial/technical highlights"""
        title = (article.get("title") or "").strip()
        financial_amounts = info.get("financial_amounts", [])
        technical_specs = info.get("technical_specs", [])
        
        if not title:
            return "Bitcoin mining news update"
        
        # Enhance title with key metrics
        enhancements = []
        if financial_amounts:
            enhancements.extend(financial_amounts[:1])  # Use first financial amount
        if technical_specs:
            enhancements.extend(technical_specs[:1])   # Use first technical spec
        
        if enhancements:
            key_info = " | ".join(enhancements)
            enhanced_title = f"{title} - {key_info}"
        else:
            enhanced_title = title
        
        # Add emoji and ensure length compliance
        prefix = random.choice(BotConstants.TWEET_PREFIXES)
        max_title_length = BotConstants.TWEET_MAX_LENGTH - len(prefix)
        
        if len(enhanced_title) > max_title_length:
            enhanced_title = enhanced_title[:max_title_length - 3] + "..."
        
        return f"{prefix}{enhanced_title}"

    @staticmethod
    def _create_basic_tweet(article: Dict[str, Any]) -> str:
        """Create basic enhanced tweet when no special info is available"""
        title = (article.get("title") or "").strip()
        
        if not title:
            return "Bitcoin mining news update"
        
        # Add emoji prefix
        prefix = random.choice(BotConstants.TWEET_PREFIXES)
        max_title_length = BotConstants.TWEET_MAX_LENGTH - len(prefix)
        
        if len(title) > max_title_length:
            title = title[:max_title_length - 3] + "..."
        
        return f"{prefix}{title}"


class TextUtils:
    """Text processing utility functions"""
    
    # Abbreviations to save characters - optimized for Twitter readability
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
        "company": "co",
        "Company": "Co",
        "investment": "invest",
        "Investment": "Invest",
        "operations": "ops",
        "Operations": "Ops",
        "facility": "facility",  # Keep this readable
        "mining": "mining",  # Keep this as key term
        "announce": "announces",
        "announces": "announces",  # Keep for clarity
        "partnership": "partnership",  # Keep for clarity
        "United States": "US",
        "government": "govt",
        "Government": "Govt"
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
            # Known companies first (highest priority)
            r'\b(CleanSpark|Marathon Digital|Riot Platforms|MicroStrategy|Tesla|Core Scientific|Hive Blockchain|Bitfarms|Argo Blockchain|Hut 8|Canaan|Bitmain|IREN|DL Holdings?)\b',  
            # Corporate entities - be more restrictive
            r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})\s+(?:Holdings?|Corporation|Corp|Inc|LLC|Ltd)\b',  
            # Simple holding pattern
            r'\b([A-Z][a-zA-Z]{2,15})\s+Holdings?\b',  
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean up the match and avoid nonsensical extractions
                if (match and len(match) > 2 and len(match) <= 30 and 
                    match.lower() not in [c.lower() for c in companies]):
                    
                    # Filter out words that aren't company names
                    skip_words = ['stole', 'steal', 'boss', 'chief', 'head', 'arrest', 'charge', 
                                'million', 'investment', 'bitcoin', 'mining', 'new', 'first', 
                                'facility', 'energy', 'strategic', 'partnership']
                    
                    if not any(word in match.lower() for word in skip_words):
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
        return TweetFormatter.create_enhanced_tweet_text(article)

    @staticmethod
    def _filter_repetitive_content(summary: str, hook_tweet: str, article: Dict[str, Any]) -> str:
        if any(word in title_lower for word in ["expand", "expansion"]):
            emoji = "📈"
            action = "expands"
        elif any(word in title_lower for word in ["launch", "start"]):
            emoji = "🚀"
            action = "launches"
        elif any(word in title_lower for word in ["partner", "partnership"]):
            emoji = "🤝"
            action = "partners w/"
        elif any(word in title_lower for word in ["acquire", "acquisition"]):
            emoji = "💰"
            action = "acquires"
        else:
            action = "invests"
        
        components.extend([emoji, primary_company, action])
        
        # Financial amount (prioritize dollar amounts)
        if info["financial_amounts"]:
            dollar_amounts = [a for a in info["financial_amounts"] if '$' in a]
            if dollar_amounts:
                components.append(dollar_amounts[0])
            else:
                components.append(info["financial_amounts"][0])
        
        components.append("in BTC mining")
        
        # Partner company (only if we have a second distinct company)
        if len(info["companies"]) > 1:
            second_company = info["companies"][1]
            if len(second_company) <= 20 and second_company.lower() != primary_company.lower():
                components.append(f"w/ {second_company}")
        
        # Technical specs as additional context
        if info["technical_specs"]:
            base_text = " ".join(components)
            tech_detail = info["technical_specs"][0]
            
            # Choose appropriate label
            if "annually" in tech_detail or "/yr" in tech_detail or "per year" in tech_detail:
                full_text = f"{base_text}. Target: {tech_detail}"
            else:
                full_text = f"{base_text}. Specs: {tech_detail}"
            
            # Apply abbreviations and check length
            full_text = TextUtils._apply_abbreviations(full_text)
            if len(full_text) <= BotConstants.TWEET_MAX_LENGTH:
                return full_text
        
        # Return base text with abbreviations applied (no hashtags)
        base_text = " ".join(components)
        return TextUtils._apply_abbreviations(base_text)
    
    @staticmethod
    def _create_news_focused_tweet(info: Dict[str, Any], title: str) -> str:
        """Create news-focused format for regulatory/general news with better readability"""
        # Add appropriate emoji for news type
        title_lower = title.lower()
        emoji = "📰"
        
        if any(word in title_lower for word in ["approve", "approved", "approval"]):
            emoji = "✅"
        elif any(word in title_lower for word in ["regulation", "regulatory", "rule"]):
            emoji = "⚖️"
        elif any(word in title_lower for word in ["ban", "banned", "restrict"]):
            emoji = "🚫"
        elif any(word in title_lower for word in ["sec", "cftc", "government"]):
            emoji = "🏛️"
        
        # Start with emoji
        enhanced_title = f"{emoji} {title}"
        
        # Add financial context if available and significant
        if info["financial_amounts"]:
            # Only add if it's a significant amount not already prominently featured
            amount = info["financial_amounts"][0]
            if '$' in amount and 'million' in amount.lower() or 'billion' in amount.lower():
                if not any(amt.replace('$', '').replace(',', '') in title for amt in info["financial_amounts"]):
                    enhanced_title = f"{emoji} {amount}: {title}"
        
        # Apply abbreviations (no hashtags)
        enhanced_title = TextUtils._apply_abbreviations(enhanced_title)
        
        # Ensure length compliance
        if len(enhanced_title) > BotConstants.TWEET_MAX_LENGTH:
            enhanced_title = enhanced_title[:BotConstants.TWEET_TRUNCATE_LENGTH] + "..."
        
        return enhanced_title
    
    @staticmethod
    def _create_enhanced_generic_tweet(info: Dict[str, Any], title: str) -> str:
        """Create enhanced generic format with better readability and structure"""
        title_lower = title.lower()
        
        # Determine appropriate emoji based on content
        emoji = "📰"  # Default news emoji
        
        if any(word in title_lower for word in ["milestone", "reaches", "production"]):
            emoji = "🎯"
        elif any(word in title_lower for word in ["relocat", "move", "transfer"]):
            emoji = "🌍"
        elif any(word in title_lower for word in ["facility", "farm", "center"]):
            emoji = "🏭"
        elif any(word in title_lower for word in ["invest", "fund", "capital"]):
            emoji = "💰"
        elif any(word in title_lower for word in ["tech", "hash", "power", "energy"]):
            emoji = "⚡"
        
        components = [emoji]
        
        # Add location context if significant and not already in title
        if info["locations"]:
            location = info["locations"][0].title()
            if location.lower() not in title_lower and len(location) <= 15:
                components.append(f"{location}:")
        
        # Add financial amount if significant and not prominently featured
        if info["financial_amounts"]:
            amount = info["financial_amounts"][0]
            # Only add if it's a substantial amount
            if ('$' in amount and ('million' in amount.lower() or 'billion' in amount.lower())) or 'BTC' in amount:
                if not any(amt.replace('$', '').replace(',', '') in title for amt in info["financial_amounts"][:1]):
                    components.append(f"{amount}:")
        
        # Add the title
        components.append(title)
        
        # Combine and apply abbreviations (no hashtags)
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
    def _enhance_gemini_headline(gemini_headline: str, article: Dict[str, Any]) -> str:
        """Add minimal visual enhancements to Gemini-generated headlines (1 emoji max, no hashtags)"""
        # Extract info for context-aware emoji selection
        info = TextUtils.extract_key_info(article)
        title_lower = gemini_headline.lower()
        
        # Add appropriate emoji based on content (only if not already present and max 1)
        if not any(emoji in gemini_headline for emoji in ['🏢', '🤝', '✅', '🎯', '🌍', '📰', '⚡', '🏭', '💰', '📈']):
            emoji = ""
            if any(word in title_lower for word in ["partner", "partnership", "collaborate"]):
                emoji = "🤝 "
            elif any(word in title_lower for word in ["invest", "fund", "capital", "million", "billion"]):
                emoji = "💰 "
            elif any(word in title_lower for word in ["expand", "expansion", "growth", "increase"]):
                emoji = "📈 "
            elif any(word in title_lower for word in ["approve", "approved", "approval"]):
                emoji = "✅ "
            elif any(word in title_lower for word in ["milestone", "reaches", "achievement"]):
                emoji = "🎯 "
            elif any(word in title_lower for word in ["facility", "farm", "center", "plant"]):
                emoji = "🏭 "
            elif any(word in title_lower for word in ["energy", "power", "hashrate", "mining"]):
                emoji = "⚡ "
            elif any(word in title_lower for word in ["relocat", "move", "transfer"]):
                emoji = "🌍 "
            else:
                emoji = "📰 "
            
            gemini_headline = f"{emoji}{gemini_headline}"
        
        # No hashtags as per user request
        return gemini_headline

    @staticmethod
    def _filter_repetitive_content(summary: str, hook_tweet: str, article: Dict[str, Any]) -> str:
        """Filter out content from summary that's already mentioned in hook tweet"""
        return ContentFilter.filter_repetitive_content(summary, hook_tweet, article)
    
    @staticmethod
    def _extract_unique_summary_info(article: Dict[str, Any], hook_tweet: str) -> str:
        """Extract unique information for summary when Gemini summary is too repetitive"""
        info = TextUtils.extract_key_info(article)
        hook_lower = hook_tweet.lower()
        
        unique_points = []
        
        # Look for technical specs not mentioned in hook
        for spec in info.get("technical_specs", []):
            if spec.lower() not in hook_lower:
                unique_points.append(f"▪ {spec}")
        
        # Look for locations not mentioned in hook
        for location in info.get("locations", []):
            if location.lower() not in hook_lower:
                unique_points.append(f"▪ {location}")
        
        # Look for regulatory info not mentioned in hook
        for reg in info.get("regulatory", []):
            if reg.lower() not in hook_lower:
                unique_points.append(f"▪ {reg}")
        
        # Look for additional financial amounts not in hook
        for amount in info.get("financial_amounts", []):
            amount_normalized = amount.replace('$', '').replace(',', '').lower()
            if amount_normalized not in hook_lower and amount.lower() not in hook_lower:
                unique_points.append(f"▪ {amount}")
        
        # Return up to 3 unique points
        if unique_points:
            return '\n'.join(unique_points[:3])
        else:
            return ""

    @staticmethod
    def create_hook_tweet(article: Dict[str, Any]) -> str:
        """Create the hook/benefit tweet that leads the thread, using Gemini AI when available."""
        # Handle None article input defensively
        if article is None:
            logger.warning("Received None article in create_hook_tweet, using fallback")
            return "Bitcoin mining news update"
        
        # If we have Gemini-generated content, use it directly with light formatting
        gemini_headline = article.get("gemini_headline", "") or ""
        
        if gemini_headline and gemini_headline.strip():
            # Gemini content is already optimized, just apply minimal enhancements
            enhanced_gemini = TextUtils._enhance_gemini_headline(gemini_headline, article)
            if len(enhanced_gemini) <= BotConstants.TWEET_MAX_LENGTH:
                return enhanced_gemini
        
        # Fallback to our enhanced formatting for non-Gemini content
        return TextUtils.create_enhanced_tweet_text(article)

    @staticmethod
    def create_summary_tweet(article: Dict[str, Any]) -> str:
        """Create a summary tweet with Gemini summary (no URL), avoiding repetition with hook tweet."""
        # Handle None article input defensively
        if article is None:
            logger.warning("Received None article in create_summary_tweet, returning empty")
            return ""

        # Get the hook tweet to check for repetition
        hook_tweet = TextUtils.create_hook_tweet(article)
        
        # Use Gemini-generated summary for the summary tweet (no URL)
        gemini_summary = article.get("gemini_summary", "") or ""
        
        if gemini_summary and gemini_summary.strip():
            # Clean up the summary format (remove bullet points for better readability)
            clean_summary = gemini_summary.replace("Key highlights:\n", "").replace("•", "▪").strip()
            
            # Check for repetition and create a filtered summary
            filtered_summary = TextUtils._filter_repetitive_content(clean_summary, hook_tweet, article)
            
            if filtered_summary:
                # Ensure summary fits within character limit
                if len(filtered_summary) <= BotConstants.TWEET_MAX_LENGTH:
                    return filtered_summary
                else:
                    # Truncate summary to fit
                    return filtered_summary[:BotConstants.TWEET_TRUNCATE_LENGTH] + "..."
            else:
                # If everything was filtered out, return empty
                return ""
        else:
            # No Gemini summary available, return empty string
            return ""

    @staticmethod  
    def create_url_tweet(article: Dict[str, Any]) -> str:
        """Create a standalone URL tweet."""
        # Handle None article input defensively
        if article is None:
            logger.warning("Received None article in create_url_tweet, returning empty")
            return ""
            
        url = (article.get("url") or article.get("uri") or "").strip()
        if not url:
            return ""

        # Return just the URL
        return url

    @staticmethod
    def create_link_tweet(article: Dict[str, Any]) -> str:
        """Create the succinct link tweet with Gemini summary or call-to-action."""
        # Handle None article input defensively
        if article is None:
            logger.warning("Received None article in create_link_tweet, returning empty")
            return ""
            
        url = (article.get("url") or article.get("uri") or "").strip()
        if not url:
            return ""

        # Prefer Gemini-generated summary for the second tweet
        gemini_summary = article.get("gemini_summary", "") or ""
        
        if gemini_summary and gemini_summary.strip():
            # Get the hook tweet to check for repetition
            hook_tweet = TextUtils.create_hook_tweet(article)
            
            # Use Gemini summary with URL
            # Clean up the summary format (remove bullet points for better readability)
            clean_summary = gemini_summary.replace("Key highlights:\n", "").replace("•", "▪").strip()
            
            # Check for repetition and create a filtered summary
            filtered_summary = TextUtils._filter_repetitive_content(clean_summary, hook_tweet, article)
            
            if filtered_summary:
                # Try to fit filtered summary + URL within character limit
                max_summary_length = BotConstants.TWEET_MAX_LENGTH - len(url) - 10  # Reserve space for URL and spacing
                
                if len(filtered_summary) <= max_summary_length:
                    link_tweet = f"{filtered_summary}\n\n{url}"
                else:
                    # Truncate filtered summary to fit with URL
                    truncated_summary = filtered_summary[:max_summary_length - 3] + "..."
                    link_tweet = f"{truncated_summary}\n\n{url}"
            else:
                # If everything was filtered out, fallback to just URL with call-to-action
                call_to_action = getattr(BotConstants, "TWEET_CALL_TO_ACTION", "Read more:").strip()
                if call_to_action:
                    link_tweet = f"{call_to_action} {url}".strip()
                else:
                    link_tweet = url
        else:
            # Fallback to traditional call-to-action format
            call_to_action = getattr(BotConstants, "TWEET_CALL_TO_ACTION", "Read more:").strip()
            if call_to_action:
                link_tweet = f"{call_to_action} {url}".strip()
            else:
                link_tweet = url

        # Final length check
        if len(link_tweet) > BotConstants.TWEET_MAX_LENGTH:
            if len(url) <= BotConstants.TWEET_MAX_LENGTH:
                return url[:BotConstants.TWEET_MAX_LENGTH]
            return url[:BotConstants.TWEET_TRUNCATE_LENGTH] + "..."

        return link_tweet

    @staticmethod
    def create_three_part_thread(article: Dict[str, Any]) -> Tuple[str, str, str]:
        """Return three tweets for a three-part thread: hook, summary, url."""
        # Handle None article input defensively
        if article is None:
            logger.warning("Received None article in create_three_part_thread, using fallback")
            return "Bitcoin mining news update", "", ""
            
        # Create hook tweet (headline with emoji)
        hook_tweet = TextUtils.create_hook_tweet(article)
        
        # Create summary tweet (Gemini summary without URL)
        summary_tweet = TextUtils.create_summary_tweet(article)
        
        # Create URL tweet (just the URL)
        url_tweet = TextUtils.create_url_tweet(article)
        
        return hook_tweet, summary_tweet, url_tweet

    @staticmethod
    def create_thread_texts(article: Dict[str, Any]) -> Tuple[str, str]:
        """Return both tweets for a two-part thread (for backward compatibility)."""
        if article is None:
            logger.warning("Received None article in create_thread_texts, using fallback")
            return "Bitcoin mining news update", ""
            
        # Create hook tweet and check for URL duplication
        hook_tweet = TextUtils.create_hook_tweet(article)
        
        # Remove URL from hook tweet if present
        hook_tweet = TextUtils._remove_url_from_text(hook_tweet, article)
        
        # Create link tweet 
        link_tweet = TextUtils.create_link_tweet(article)
        
        return hook_tweet, link_tweet

    @staticmethod
    def _remove_url_from_text(text: str, article: Dict[str, Any]) -> str:
        """Remove URL from text if present"""
        url = (article.get("url") or article.get("uri") or "").strip()
        if url and url in text:
            # Remove URL from text - find URL and everything after it
            url_index = text.find(url)
            if url_index != -1:
                # Keep everything before the URL, strip trailing whitespace and prepositions
                text = text[:url_index].strip()
                # Remove trailing prepositions
                for word in TextPatterns.TRAILING_WORDS:
                    if text.lower().endswith(f" {word}"):
                        text = text[:-len(word)-1].strip()
                        break
        return text

    @staticmethod
    def _create_intelligent_thread(article: Dict[str, Any]) -> Tuple[str, str]:
        """Create an intelligent thread when content is too long to fit in a single tweet."""
        # Get the title and URL
        title = article.get("title", "").strip()
        url = (article.get("url") or article.get("uri") or "").strip()
        
        # Extract key information for context
        info = TextUtils.extract_key_info(article)
        
        # Strategy: Split title intelligently at natural break points
        # Try to create a compelling first tweet that doesn't get cut off
        
        # Remove excessive punctuation and normalize spaces
        clean_title = re.sub(r'\s+', ' ', title).strip()
        
        # Apply abbreviations first to save space
        abbreviated_title = TextUtils._apply_abbreviations(clean_title)
        
        # If abbreviated title fits, use it as is
        if len(abbreviated_title) <= BotConstants.TWEET_MAX_LENGTH:
            first_tweet = abbreviated_title
            # Create informative second tweet with URL
            second_tweet = TextUtils.create_link_tweet(article)
            return first_tweet, second_tweet
        
        # Title is still too long even with abbreviations
        # Find intelligent split points (prefer after sentences, then clauses, then words)
        
        # Try splitting at sentence boundaries first
        sentences = re.split(r'[.!?]\s+', abbreviated_title)
        if len(sentences) > 1:
            first_part = sentences[0]
            if len(first_part) <= BotConstants.TWEET_MAX_LENGTH - 10:  # Leave room for "... (1/2)"
                remaining = ' '.join(sentences[1:])
                first_tweet = f"{first_part}... (1/2)"
                
                # Create second tweet with remaining content and URL
                if url:
                    if len(remaining) + len(url) + 15 <= BotConstants.TWEET_MAX_LENGTH:  # Room for "(2/2) " and " "
                        second_tweet = f"(2/2) {remaining} {url}"
                    else:
                        # Truncate remaining if needed
                        max_remaining = BotConstants.TWEET_MAX_LENGTH - len(url) - 15
                        if len(remaining) > max_remaining:
                            remaining = remaining[:max_remaining].rsplit(' ', 1)[0] + "..."
                        second_tweet = f"(2/2) {remaining} {url}"
                else:
                    second_tweet = f"(2/2) {remaining}"
                
                return first_tweet, second_tweet
        
        # No good sentence break, try splitting at clause boundaries (commas, "with", "and")
        clause_patterns = [r'\s+with\s+', r'\s+and\s+', r',\s+', r'\s+including\s+', r'\s+across\s+']
        for pattern in clause_patterns:
            parts = re.split(pattern, abbreviated_title, maxsplit=1)
            if len(parts) == 2:
                first_part = parts[0]
                if len(first_part) <= BotConstants.TWEET_MAX_LENGTH - 10:
                    remaining = parts[1]
                    first_tweet = f"{first_part}... (1/2)"
                    
                    # Create second tweet with remaining content and URL
                    if url:
                        if len(remaining) + len(url) + 15 <= BotConstants.TWEET_MAX_LENGTH:
                            second_tweet = f"(2/2) {remaining} {url}"
                        else:
                            max_remaining = BotConstants.TWEET_MAX_LENGTH - len(url) - 15
                            if len(remaining) > max_remaining:
                                remaining = remaining[:max_remaining].rsplit(' ', 1)[0] + "..."
                            second_tweet = f"(2/2) {remaining} {url}"
                    else:
                        second_tweet = f"(2/2) {remaining}"
                    
                    return first_tweet, second_tweet
        
        # Last resort: split at word boundary
        words = abbreviated_title.split()
        if len(words) > 1:
            # Find the longest prefix that fits
            first_words = []
            char_count = 0
            for word in words:
                if char_count + len(word) + 1 + 10 <= BotConstants.TWEET_MAX_LENGTH:  # +1 for space, +10 for "... (1/2)"
                    first_words.append(word)
                    char_count += len(word) + 1
                else:
                    break
            
            if first_words:
                first_part = ' '.join(first_words)
                remaining_words = words[len(first_words):]
                remaining = ' '.join(remaining_words)
                
                first_tweet = f"{first_part}... (1/2)"
                
                # Create second tweet with remaining content and URL
                if url:
                    if len(remaining) + len(url) + 15 <= BotConstants.TWEET_MAX_LENGTH:
                        second_tweet = f"(2/2) {remaining} {url}"
                    else:
                        max_remaining = BotConstants.TWEET_MAX_LENGTH - len(url) - 15
                        if len(remaining) > max_remaining:
                            remaining = remaining[:max_remaining].rsplit(' ', 1)[0] + "..."
                        second_tweet = f"(2/2) {remaining} {url}"
                else:
                    if len(remaining) + 6 > BotConstants.TWEET_MAX_LENGTH:  # +6 for "(2/2) "
                        remaining = remaining[:BotConstants.TWEET_MAX_LENGTH - 9].rsplit(' ', 1)[0] + "..."  # +9 for "(2/2) ..."
                    second_tweet = f"(2/2) {remaining}"
                
                return first_tweet, second_tweet
        
        # Fallback: Just truncate and add URL to second tweet
        first_tweet = abbreviated_title[:BotConstants.TWEET_MAX_LENGTH - 10] + "... (1/2)"
        if url:
            second_tweet = f"(2/2) {url}"
        else:
            second_tweet = "(2/2) [continued]"
        
        return first_tweet, second_tweet

    @staticmethod
    def create_tweet_text(article: Dict[str, Any]) -> str:
        """Create catchy tweet text for the article (enhanced version)"""
        # Handle None article input defensively
        if article is None:
            logger.warning("Received None article in create_tweet_text, using fallback")
            return "Bitcoin mining news update"
            
        # Use the enhanced method by default
        return TextUtils.create_hook_tweet(article)
    
    @staticmethod
    def create_original_tweet_text(article: Dict[str, Any]) -> str:
        """Original tweet text creation method (kept for fallback)"""
        try:
            # Handle None article input defensively
            if article is None:
                logger.warning("Received None article in original tweet text creation, using fallback")
                return "Bitcoin mining news update"
                
            # Choose a catchy prefix
            prefix = random.choice(BotConstants.TWEET_PREFIXES)

            # Create a summary (use Gemini headline if available and meaningful, otherwise article title)
            gemini_headline = article.get("gemini_headline", "") or ""
            original_title = article.get("title", "") or ""
            
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