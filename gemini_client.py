"""
Gemini AI client for Bitcoin Mining News Bot
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

import google.generativeai as genai

from config import GeminiConfig

logger = logging.getLogger('bitcoin_mining_bot')


class GeminiClient:
    """Wrapper for Google Gemini AI client"""
    
    def __init__(self, config: GeminiConfig):
        """Initialize Gemini client"""
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Gemini AI client initialized successfully")
    
    def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a news article using Gemini AI
        
        Args:
            article: Article dictionary containing title, body, url, etc.
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Extract article information
            title = article.get('title', 'No title')
            body = article.get('body', article.get('summary', 'No content'))
            url = article.get('url', article.get('uri', 'No URL'))
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(title, body, url)
            
            # Generate analysis
            logger.info(f"Analyzing article: {title[:50]}...")
            response = self.model.generate_content(prompt)
            
            # Return structured analysis
            analysis = {
                'article_title': title,
                'article_url': url,
                'analysis_text': response.text,
                'analysis_timestamp': datetime.now().isoformat(),
                'model_used': 'gemini-1.5-flash'
            }
            
            logger.info("Article analysis completed successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze article: {str(e)}")
            return {
                'article_title': article.get('title', 'Unknown'),
                'article_url': article.get('url', article.get('uri', 'No URL')),
                'analysis_text': f"Analysis failed: {str(e)}",
                'analysis_timestamp': datetime.now().isoformat(),
                'model_used': 'gemini-1.5-flash',
                'error': True
            }
    
    def _create_analysis_prompt(self, title: str, body: str, url: str) -> str:
        """Create a detailed analysis prompt for the article"""
        prompt = f"""
Analyze the following Bitcoin mining news article and provide a comprehensive analysis:

**Article Title:** {title}

**Article Content:** {body[:2000]}...

**Article URL:** {url}

Please provide a detailed analysis covering:

1. **Key Points Summary**: Main points and developments mentioned in the article

2. **Bitcoin Mining Impact**: How this news affects the Bitcoin mining industry specifically

3. **Market Implications**: Potential impact on Bitcoin mining companies, hashrate, difficulty, or mining economics

4. **Technical Analysis**: Any technical aspects related to mining hardware, software, or infrastructure

5. **Regulatory/Policy Implications**: Any regulatory or policy implications for Bitcoin mining

6. **Future Outlook**: What this means for the future of Bitcoin mining

7. **Investment Considerations**: Potential implications for Bitcoin mining investments

Format your response in clear, well-structured markdown with appropriate headings and bullet points.
"""
        return prompt


class ReportGenerator:
    """Generates and saves markdown reports for analyzed articles"""
    
    def __init__(self, reports_dir: str = "reports"):
        """Initialize report generator"""
        self.reports_dir = reports_dir
        self._ensure_reports_directory()
    
    def _ensure_reports_directory(self):
        """Ensure the reports directory exists"""
        os.makedirs(self.reports_dir, exist_ok=True)
        logger.info(f"Reports directory ensured: {self.reports_dir}")
    
    def save_analysis_report(self, analysis: Dict[str, Any]) -> Optional[str]:
        """
        Save analysis report as markdown file
        
        Args:
            analysis: Analysis results from Gemini
            
        Returns:
            Path to saved report file, or None if failed
        """
        try:
            # Generate filename based on article title and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            title_slug = self._create_filename_slug(analysis['article_title'])
            filename = f"{timestamp}_{title_slug}.md"
            filepath = os.path.join(self.reports_dir, filename)
            
            # Generate markdown content
            markdown_content = self._generate_markdown_report(analysis)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Analysis report saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save analysis report: {str(e)}")
            return None
    
    def _create_filename_slug(self, title: str) -> str:
        """Create a safe filename slug from article title"""
        import re
        # Remove special characters and limit length
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '_', slug)
        return slug[:50]  # Limit length
    
    def _generate_markdown_report(self, analysis: Dict[str, Any]) -> str:
        """Generate markdown content for the analysis report"""
        timestamp = analysis.get('analysis_timestamp', datetime.now().isoformat())
        model = analysis.get('model_used', 'Unknown')
        
        markdown = f"""# Bitcoin Mining News Analysis Report

## Article Information
- **Title**: {analysis['article_title']}
- **URL**: {analysis['article_url']}
- **Analysis Date**: {timestamp}
- **AI Model**: {model}

---

## AI Analysis

{analysis['analysis_text']}

---

*This report was automatically generated by the Bitcoin Mining News Bot using AI analysis.*
"""
        return markdown