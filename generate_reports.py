#!/usr/bin/env python3
"""
Generate Gemini AI Reports for Posted Articles
----------------------------------------------
This script generates analysis reports for recently posted articles using Gemini AI.
It's designed to run as a separate workflow from the main Twitter posting workflow.
"""

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('gemini_report_generator')

# Import bot components
from config import BotConstants
from gemini_client import GeminiClient, ReportGenerator
from utils import FileManager


class GeminiReportGenerator:
    """Standalone Gemini report generator for posted articles"""
    
    def __init__(self):
        """Initialize the report generator"""
        self.report_generator = ReportGenerator()
        self.gemini_client = None
        
        # Try to initialize Gemini client
        try:
            from config import GeminiConfig
            gemini_config = GeminiConfig.from_env()
            self.gemini_client = GeminiClient(gemini_config)
            logger.info("Gemini client initialized successfully")
        except ValueError as e:
            logger.warning(f"Gemini client not initialized: {str(e)}")
    
    def get_recent_articles_needing_reports(self, hours_back: int = 2) -> List[Dict[str, Any]]:
        """Get recently posted articles that need Gemini analysis reports"""
        try:
            # Load posted articles
            posted_articles_data = FileManager.load_posted_articles()
            queued_articles = posted_articles_data.get('queued_articles', [])
            
            # Find articles posted in the last few hours that don't have reports yet
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            recent_articles = []
            
            for article in queued_articles:
                # Check if article was recently processed and needs a report
                if self._article_needs_report(article):
                    recent_articles.append(article)
            
            logger.info(f"Found {len(recent_articles)} articles needing Gemini reports")
            return recent_articles
            
        except Exception as e:
            logger.error(f"Error loading recent articles: {str(e)}")
            return []
    
    def _article_needs_report(self, article: Dict[str, Any]) -> bool:
        """Check if an article needs a Gemini analysis report"""
        title = article.get('title', 'Unknown title')
        
        # Check if report already exists for this article
        # Simple check: look for report files with similar title
        try:
            reports_dir = "files/reports"
            if not os.path.exists(reports_dir):
                return True
                
            # Create a simple slug from the title for matching
            title_slug = self._create_title_slug(title)
            
            # Check if any report file contains this slug
            for filename in os.listdir(reports_dir):
                if title_slug in filename.lower():
                    logger.debug(f"Report already exists for: {title[:50]}...")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking existing reports: {str(e)}")
            return True
    
    def _create_title_slug(self, title: str) -> str:
        """Create a simple slug from article title for matching"""
        import re
        # Remove special characters and convert to lowercase
        slug = re.sub(r'[^a-zA-Z0-9\s]', '', title.lower())
        # Replace spaces with underscores and limit length
        slug = re.sub(r'\s+', '_', slug)[:30]
        return slug
    
    def generate_report_for_article(self, article: Dict[str, Any]) -> bool:
        """Generate a Gemini analysis report for a single article"""
        if not self.gemini_client:
            logger.warning("Gemini client not available, skipping report generation")
            return False
        
        try:
            title = article.get('title', 'Unknown title')
            logger.info(f"Generating Gemini report for: {title[:50]}...")
            
            # Analyze article with Gemini AI
            analysis = self.gemini_client.analyze_article(article)
            
            # Save report
            report_path = self.report_generator.save_analysis_report(analysis)
            
            if report_path:
                logger.info(f"Successfully generated report: {os.path.basename(report_path)}")
                return True
            else:
                logger.error(f"Failed to save report for: {title[:50]}...")
                return False
                
        except Exception as e:
            logger.error(f"Error generating report for article: {str(e)}")
            return False
    
    def run(self) -> None:
        """Main method to generate reports for recent articles"""
        logger.info("Starting Gemini report generation...")
        
        if not self.gemini_client:
            logger.error("Gemini client not available - cannot generate reports")
            return
        
        # Get recent articles needing reports
        recent_articles = self.get_recent_articles_needing_reports()
        
        if not recent_articles:
            logger.info("No recent articles need Gemini reports")
            return
        
        # Generate reports for each article
        successful_reports = 0
        for article in recent_articles:
            if self.generate_report_for_article(article):
                successful_reports += 1
        
        logger.info(f"Generated {successful_reports}/{len(recent_articles)} Gemini reports successfully")


def main():
    """Main entry point"""
    try:
        generator = GeminiReportGenerator()
        generator.run()
    except Exception as e:
        logger.error(f"Error in Gemini report generation: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())