#!/usr/bin/env python3
"""
Runtime logging module for Bitcoin Mining News Bot.
Tracks blocked content, failed posts, and runtime issues for debugging.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger('bitcoin_mining_bot')

class RuntimeLogger:
    """Handles runtime logging and blocked content tracking."""
    
    def __init__(self, logs_dir: str = "/home/runner/work/_temp/runtime-logs"):
        """Initialize the runtime logger.
        
        Args:
            logs_dir: Directory for runtime logs (defaults to GitHub Actions temp path)
        """
        self.logs_dir = logs_dir
        self.blocked_jsonl_path = os.path.join(logs_dir, "blocked.jsonl")
        self.blocked_md_path = os.path.join(logs_dir, "blocked.md")
        
        # Create logs directory if it doesn't exist
        os.makedirs(logs_dir, exist_ok=True)
        
        # Initialize blocked content tracking
        self.blocked_content = []
        self.session_start = datetime.now()
        
        logger.info(f"Runtime logger initialized. Logs will be saved to: {logs_dir}")
    
    def log_blocked_article(self, article: Dict[str, Any], reason: str, details: Optional[Dict] = None):
        """Log an article that was blocked/filtered.
        
        Args:
            article: Article dictionary that was blocked
            reason: Reason for blocking (e.g., "crypto_filter", "rate_limit", "duplicate")
            details: Additional details about the blocking
        """
        blocked_entry = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "title": article.get("title", "Unknown"),
            "url": article.get("url", ""),
            "uri": article.get("uri", ""),
            "source": article.get("source", {}).get("title", "Unknown"),
            "details": details or {}
        }
        
        self.blocked_content.append(blocked_entry)
        
        # Append to JSONL file immediately for real-time tracking
        try:
            with open(self.blocked_jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(blocked_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write to blocked.jsonl: {e}")
    
    def log_crypto_filtered_articles(self, excluded_details: List[Dict]):
        """Log articles filtered due to non-Bitcoin cryptocurrency mentions.
        
        Args:
            excluded_details: List of excluded article details from crypto filter
        """
        for detail in excluded_details:
            self.log_blocked_article(
                article=detail.get("article", {}),
                reason="crypto_filter",
                details={
                    "unwanted_cryptos_found": detail.get("unwanted_cryptos", []),
                    "filter_type": "cryptocurrency_mention"
                }
            )
        
        if excluded_details:
            logger.info(f"Logged {len(excluded_details)} crypto-filtered articles to runtime logs")
    
    def log_rate_limited_article(self, article: Dict[str, Any], rate_limit_details: Optional[Dict] = None):
        """Log an article that couldn't be posted due to rate limiting.
        
        Args:
            article: Article that failed to post due to rate limits
            rate_limit_details: Details about the rate limit
        """
        self.log_blocked_article(
            article=article,
            reason="rate_limit",
            details=rate_limit_details or {"type": "twitter_api_rate_limit"}
        )
    
    def log_failed_post(self, article: Dict[str, Any], error: str):
        """Log an article that failed to post due to an error.
        
        Args:
            article: Article that failed to post
            error: Error message
        """
        self.log_blocked_article(
            article=article,
            reason="post_failure",
            details={"error": error}
        )
    
    def log_duplicate_article(self, article: Dict[str, Any]):
        """Log an article that was skipped as duplicate.
        
        Args:
            article: Article that was already posted
        """
        self.log_blocked_article(
            article=article,
            reason="duplicate",
            details={"type": "already_posted"}
        )
    
    def generate_markdown_summary(self):
        """Generate a human-readable markdown summary of blocked content."""
        if not self.blocked_content:
            summary = "# Runtime Logs Summary\n\nNo blocked content recorded in this session.\n"
        else:
            # Group by reason
            by_reason = {}
            for entry in self.blocked_content:
                reason = entry["reason"]
                if reason not in by_reason:
                    by_reason[reason] = []
                by_reason[reason].append(entry)
            
            summary = f"""# Runtime Logs Summary

**Session Started:** {self.session_start.isoformat()}
**Total Blocked Articles:** {len(self.blocked_content)}

## Breakdown by Reason

"""
            
            for reason, entries in by_reason.items():
                summary += f"### {reason.replace('_', ' ').title()} ({len(entries)} articles)\n\n"
                
                for entry in entries[:5]:  # Show first 5 for each category
                    summary += f"- **{entry['title'][:80]}{'...' if len(entry['title']) > 80 else ''}**\n"
                    summary += f"  - Source: {entry['source']}\n"
                    summary += f"  - Time: {entry['timestamp']}\n"
                    
                    if entry['reason'] == 'crypto_filter':
                        cryptos = entry.get('details', {}).get('unwanted_cryptos_found', [])
                        if cryptos:
                            summary += f"  - Blocked cryptos: {', '.join(cryptos[:3])}\n"
                    
                    summary += "\n"
                
                if len(entries) > 5:
                    summary += f"*... and {len(entries) - 5} more {reason.replace('_', ' ')} articles*\n\n"
        
        # Write to markdown file
        try:
            with open(self.blocked_md_path, "w", encoding="utf-8") as f:
                f.write(summary)
            logger.info(f"Generated markdown summary: {self.blocked_md_path}")
        except Exception as e:
            logger.error(f"Failed to write blocked.md: {e}")
        
        return summary
    
    def finalize_logs(self):
        """Finalize the runtime logs and generate summary."""
        self.generate_markdown_summary()
        
        # Log summary
        if self.blocked_content:
            by_reason = {}
            for entry in self.blocked_content:
                reason = entry["reason"]
                by_reason[reason] = by_reason.get(reason, 0) + 1
            
            logger.info("Runtime logging summary:")
            for reason, count in by_reason.items():
                logger.info(f"  - {reason.replace('_', ' ').title()}: {count} articles")
        else:
            logger.info("No blocked content recorded in this session")
        
        return len(self.blocked_content)