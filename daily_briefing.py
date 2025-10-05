#!/usr/bin/env python3
"""
Bitcoin Mining Daily Briefing Generator
=======================================
Advanced daily briefing system that aggregates all fetched Bitcoin mining news,
processes them with Gemini AI and Google Deep Research, and generates comprehensive
daily briefs tailored for Bitcoin miners.

Features:
- Accesses ALL daily fetched articles (published and unpublished)
- Uses Gemini 2.0 Flash Exp with native URL context
- Integrates with Google Agentspace Deep Research API
- Generates miner-focused analysis with counter-arguments
- Professional formatting with strategic insights
"""

import json
import logging
import os
import requests
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Import from existing core architecture
try:
    from core import Article, Config, Storage, GeminiClient, FullContentFetcher
except ImportError as e:
    print(f"❌ Error: Cannot import core modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('daily_briefing')


@dataclass
class ProcessedArticle:
    """Article with enhanced processing metadata."""
    title: str
    url: str
    source: str
    published_date: str
    summary: str
    key_points: List[str]
    mining_relevance_score: float
    gemini_insights: str
    full_content_available: bool = False


@dataclass
class DeepResearchResult:
    """Results from Google Agentspace Deep Research API."""
    query: str
    research_summary: str
    key_findings: List[str]
    sources: List[str]
    confidence_score: float
    metadata: Dict[str, Any]


class GoogleAgentspaceClient:
    """
    Google Agentspace API client for Deep Research functionality.
    
    IMPORTANT: Requires allowlist access to Google Agentspace APIs.
    """
    
    def __init__(self, project_id: str, app_id: str, data_store_id: Optional[str] = None):
        """
        Initialize Agentspace client.
        
        Args:
            project_id: Google Cloud Project ID
            app_id: Agentspace App ID  
            data_store_id: Optional Data Store ID for enhanced context
        """
        self.project_id = project_id
        self.app_id = app_id
        self.data_store_id = data_store_id
        self.base_url = f"https://agentspace.googleapis.com/v1/projects/{project_id}/apps/{app_id}"
        
        # Initialize with Google Cloud credentials
        # Note: This requires proper authentication setup
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup Google Cloud authentication for Agentspace API."""
        # This would typically use Google Cloud Service Account or ADC
        # For now, we'll use a placeholder that checks for the API key
        api_key = os.getenv("GOOGLE_CLOUD_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("⚠️ No Google Cloud API key found - Deep Research will use fallback")
        self.api_key = api_key
    
    async def stream_assist(self, query: str, context_data: Optional[List[str]] = None) -> DeepResearchResult:
        """
        Perform deep research using Google Agentspace streamAssist method.
        
        CRITICAL: This requires allowlist access to Google Agentspace APIs.
        
        Args:
            query: Research query for deep analysis
            context_data: Optional additional context for research
            
        Returns:
            DeepResearchResult with comprehensive research findings
        """
        try:
            # Construct the streamAssist endpoint
            endpoint = f"{self.base_url}:streamAssist"
            
            # Prepare request payload optimized for Gemini 2.5 Pro
            payload = {
                "query": query,
                "model": "gemini-2.5-pro",  # Optimized for Deep Research
                "context": {
                    "documents": context_data or [],
                    "data_store_id": self.data_store_id
                },
                "research_depth": "comprehensive",
                "include_sources": True,
                "confidence_threshold": 0.7
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Goog-User-Project": self.project_id
            }
            
            logger.info(f"🔬 Executing Deep Research query: {query[:100]}...")
            
            # Make the API call
            response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result_data = response.json()
                logger.info("✅ Deep Research completed successfully")
                
                return DeepResearchResult(
                    query=query,
                    research_summary=result_data.get("summary", ""),
                    key_findings=result_data.get("findings", []),
                    sources=result_data.get("sources", []),
                    confidence_score=result_data.get("confidence", 0.8),
                    metadata=result_data.get("metadata", {})
                )
            
            elif response.status_code == 403:
                logger.warning("🔒 Deep Research API access denied - not on allowlist")
                return self._fallback_research(query, context_data)
            
            else:
                logger.error(f"❌ Deep Research API error: {response.status_code}")
                return self._fallback_research(query, context_data)
                
        except Exception as e:
            logger.error(f"❌ Deep Research failed: {e}")
            return self._fallback_research(query, context_data)
    
    def _fallback_research(self, query: str, context_data: Optional[List[str]] = None) -> DeepResearchResult:
        """
        Fallback research using enhanced Gemini prompting (without Deep Research API).
        
        This provides enriched context analysis until Deep Research access is granted.
        """
        logger.info("🔄 Using enhanced Gemini context analysis (fallback mode)")
        
        try:
            # Use standard Gemini API for enhanced context generation
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                raise ValueError("Gemini API key required for fallback research")
            
            import google.generativeai as genai
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Enhanced context analysis prompt
            context_text = "\n".join(context_data or [])
            enhanced_prompt = f"""
            As a Bitcoin mining industry expert, provide comprehensive analysis on: {query}
            
            Context from recent Bitcoin mining news:
            {context_text}
            
            Provide a detailed analysis covering:
            1. Current market trends and implications
            2. Technical developments affecting miners
            3. Economic factors and profitability outlook
            4. Regulatory landscape and compliance considerations
            5. Strategic recommendations for mining operations
            6. Potential risks and mitigation strategies
            
            Format as a structured research summary with key findings and actionable insights.
            Focus on practical implications for Bitcoin mining businesses.
            """
            
            response = model.generate_content(enhanced_prompt)
            analysis = response.text.strip()
            
            # Parse the structured response
            key_findings = [
                line.strip("- •").strip() 
                for line in analysis.split("\n") 
                if line.strip() and (line.startswith("- ") or line.startswith("• "))
            ]
            
            return DeepResearchResult(
                query=query,
                research_summary=analysis,
                key_findings=key_findings[:10],  # Top 10 findings
                sources=["Enhanced Gemini Analysis", "Bitcoin Mining Industry Context"],
                confidence_score=0.75,  # Slightly lower than Deep Research
                metadata={
                    "method": "enhanced_gemini_fallback",
                    "model": "gemini-2.0-flash-exp",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Fallback research failed: {e}")
            return DeepResearchResult(
                query=query,
                research_summary="Unable to generate enhanced research due to API limitations.",
                key_findings=["Deep Research API access required for comprehensive analysis"],
                sources=[],
                confidence_score=0.0,
                metadata={"error": str(e)}
            )


class DailyBriefingGenerator:
    """
    Main class for generating comprehensive daily Bitcoin mining briefings.
    
    Integrates with existing bot architecture to access all fetched articles,
    processes them with Gemini AI and Deep Research, and generates professional
    daily briefs tailored for Bitcoin miners.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the daily briefing generator."""
        self.config = config or Config.from_env()
        self.storage = Storage()
        self.content_fetcher = FullContentFetcher()
        
        # Initialize AI clients
        self.gemini_client = None
        self.deep_research_client = None
        
        # Try to initialize Gemini client
        if self.config.gemini_api_key:
            try:
                self.gemini_client = GeminiClient(self.config.gemini_api_key)
                logger.info("✅ Gemini client initialized")
            except Exception as e:
                logger.warning(f"⚠️ Gemini client initialization failed: {e}")
        
        # Try to initialize Deep Research client
        project_id = os.getenv("AGENTS_PROJECT_ID")
        app_id = os.getenv("AGENTS_APP_ID") 
        data_store_id = os.getenv("AGENTS_DATA_STORE_ID")
        
        if project_id and app_id:
            try:
                self.deep_research_client = GoogleAgentspaceClient(
                    project_id=project_id,
                    app_id=app_id,
                    data_store_id=data_store_id
                )
                logger.info("✅ Deep Research client initialized")
            except Exception as e:
                logger.warning(f"⚠️ Deep Research client failed: {e}")
        else:
            logger.info("ℹ️ Deep Research not configured (requires AGENTS_PROJECT_ID and AGENTS_APP_ID)")
    
    def fetch_daily_articles(self, days_ago: int = 1) -> List[Dict[str, Any]]:
        """
        Retrieve all Bitcoin mining articles fetched within the last N days.
        
        This accesses the bot's anti-repetition system to get ALL processed articles,
        including those not published to Twitter.
        
        Args:
            days_ago: Number of days back to retrieve articles (default: 1)
            
        Returns:
            List of article dictionaries with metadata
        """
        logger.info(f"📰 Fetching articles from last {days_ago} day(s)")
        
        try:
            # Load the posted_articles.json which contains both posted and queued articles
            posted_data = self.storage.load_posted_articles("posted_articles.json")
            
            # Also check for an articles log file (we'll create this in core.py)
            articles_log = self.storage.load_json("articles_log.json", {"articles": []})
            
            # Get all articles from both sources
            all_articles = []
            cutoff_date = datetime.now() - timedelta(days=days_ago)
            
            # Add queued articles
            for article in posted_data.get("queued_articles", []):
                if self._is_article_recent(article, cutoff_date):
                    article["source_type"] = "queued"
                    all_articles.append(article)
            
            # Add articles from log (if available) - handle both old and new format
            daily_articles = articles_log.get("daily_articles", [])
            if daily_articles:
                # New format: daily_articles contains date groups
                for date_group in daily_articles:
                    for article in date_group.get("articles", []):
                        if self._is_article_recent(article, cutoff_date):
                            article["source_type"] = "logged"
                            all_articles.append(article)
            else:
                # Fallback: old format with articles directly
                for article in articles_log.get("articles", []):
                    if self._is_article_recent(article, cutoff_date):
                        article["source_type"] = "logged"
                        all_articles.append(article)
            
            # Remove duplicates based on URL
            unique_articles = {}
            for article in all_articles:
                url = article.get("url", "")
                if url and url not in unique_articles:
                    unique_articles[url] = article
                elif url in unique_articles:
                    # Keep the most recent or complete version
                    existing = unique_articles[url]
                    if self._is_article_better(article, existing):
                        unique_articles[url] = article
            
            result = list(unique_articles.values())
            logger.info(f"📊 Found {len(result)} unique articles from last {days_ago} day(s)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error fetching daily articles: {e}")
            return []
    
    def _is_article_recent(self, article: Dict[str, Any], cutoff_date: datetime) -> bool:
        """Check if article is within the specified time range."""
        try:
            date_str = article.get("dateTimePub") or article.get("dateTime") or article.get("timestamp")
            if not date_str:
                return True  # Include articles without dates
            
            article_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            return article_date >= cutoff_date
            
        except (ValueError, TypeError):
            return True  # Include articles with unparseable dates
    
    def _is_article_better(self, new_article: Dict[str, Any], existing_article: Dict[str, Any]) -> bool:
        """Determine if new article is better than existing one."""
        # Prefer logged articles over queued (they have more metadata)
        if new_article.get("source_type") == "logged" and existing_article.get("source_type") == "queued":
            return True
        
        # Prefer articles with full content
        if new_article.get("full_content") and not existing_article.get("full_content"):
            return True
        
        # Prefer more recent articles
        try:
            new_date = datetime.fromisoformat(new_article.get("dateTimePub", "1900-01-01").replace('Z', '+00:00'))
            existing_date = datetime.fromisoformat(existing_article.get("dateTimePub", "1900-01-01").replace('Z', '+00:00'))
            return new_date > existing_date
        except:
            return False
    
    def process_article_with_gemini(self, article_data: Dict[str, Any]) -> ProcessedArticle:
        """
        Process an individual article with Gemini AI for enhanced context extraction.
        
        Uses Gemini 2.0 Flash Exp with URL context for comprehensive analysis.
        
        Args:
            article_data: Raw article data dictionary
            
        Returns:
            ProcessedArticle with enhanced metadata and analysis
        """
        try:
            # Convert to Article object for processing
            article = Article.from_dict(article_data, self.content_fetcher)
            
            logger.info(f"🤖 Processing article: {article.title[:60]}...")
            
            if not self.gemini_client:
                logger.warning("⚠️ Gemini client not available - using basic processing")
                return self._basic_article_processing(article_data)
            
            # Generate comprehensive analysis using Gemini URL context
            analysis_prompt = f"""
            As a Bitcoin mining industry analyst, provide detailed analysis of this article:
            
            Title: {article.title}
            URL: {article.url}
            Source: {article.source}
            
            Please analyze and provide:
            1. 3-sentence executive summary focusing on mining implications
            2. 5 key points most relevant to Bitcoin miners
            3. Mining relevance score (0.0-1.0) based on direct impact on mining operations
            4. Strategic insights for mining businesses
            
            Use the article's full content via URL context for comprehensive analysis.
            Focus on practical implications for miners: profitability, efficiency, regulations, hardware, energy costs.
            
            Format response as JSON:
            {{
                "summary": "Executive summary...",
                "key_points": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
                "relevance_score": 0.85,
                "insights": "Strategic insights and implications..."
            }}
            """
            
            # Use URL context tools for full article access
            tools = [{"url_context": {}}] if hasattr(self.gemini_client, 'model') else []
            
            try:
                response = self.gemini_client.model.generate_content(
                    analysis_prompt,
                    tools=tools
                )
                
                # Parse JSON response
                import json
                analysis = json.loads(response.text.strip())
                
                return ProcessedArticle(
                    title=article.title,
                    url=article.url,
                    source=article.source,
                    published_date=article_data.get("dateTimePub", ""),
                    summary=analysis.get("summary", ""),
                    key_points=analysis.get("key_points", []),
                    mining_relevance_score=analysis.get("relevance_score", 0.5),
                    gemini_insights=analysis.get("insights", ""),
                    full_content_available=True
                )
                
            except json.JSONDecodeError:
                # Fallback to text parsing if JSON parsing fails
                logger.warning("⚠️ JSON parsing failed, using text extraction")
                return self._parse_text_analysis(response.text, article_data)
                
        except Exception as e:
            logger.error(f"❌ Error processing article with Gemini: {e}")
            return self._basic_article_processing(article_data)
    
    def _basic_article_processing(self, article_data: Dict[str, Any]) -> ProcessedArticle:
        """Fallback processing without AI enhancement."""
        # Handle source field - could be string or dict
        source_data = article_data.get("source", "Unknown Source")
        if isinstance(source_data, dict):
            source_name = source_data.get("title", "Unknown Source")
        else:
            source_name = str(source_data) if source_data else "Unknown Source"
            
        return ProcessedArticle(
            title=article_data.get("title", "Unknown Title"),
            url=article_data.get("url", ""),
            source=source_name,
            published_date=article_data.get("dateTimePub", ""),
            summary=article_data.get("body", "")[:300] + "...",
            key_points=[
                "Bitcoin mining industry development",
                "Market implications for miners", 
                "Technical considerations",
                "Regulatory or economic factors",
                "Future outlook for mining sector"
            ],
            mining_relevance_score=0.6,  # Default moderate relevance
            gemini_insights="Basic processing - enhanced analysis requires Gemini API",
            full_content_available=False
        )
    
    def _parse_text_analysis(self, response_text: str, article_data: Dict[str, Any]) -> ProcessedArticle:
        """Parse Gemini response when JSON parsing fails."""
        lines = response_text.split('\n')
        
        summary = "Analysis available in insights section"
        key_points = []
        relevance_score = 0.7
        insights = response_text
        
        # Try to extract structured information
        for line in lines:
            if line.strip().startswith(('•', '-', '*')):
                point = line.strip().lstrip('•-* ').strip()
                if point and len(key_points) < 5:
                    key_points.append(point)
        
        # If no bullet points found, create generic ones
        if not key_points:
            key_points = [
                "Industry development with mining implications",
                "Market dynamics affecting mining operations",
                "Technical or regulatory considerations",
                "Economic factors impacting profitability",
                "Strategic considerations for miners"
            ]
        
        return ProcessedArticle(
            title=article_data.get("title", "Unknown Title"),
            url=article_data.get("url", ""),
            source=article_data.get("source", {}).get("title", "Unknown Source"),
            published_date=article_data.get("dateTimePub", ""),
            summary=summary,
            key_points=key_points,
            mining_relevance_score=relevance_score,
            gemini_insights=insights,
            full_content_available=True
        )
    
    async def perform_deep_research(self, processed_articles: List[ProcessedArticle]) -> Optional[DeepResearchResult]:
        """
        Perform deep research using Google Agentspace API on aggregated article topics.
        
        Args:
            processed_articles: List of processed articles for context
            
        Returns:
            DeepResearchResult with comprehensive industry analysis
        """
        if not self.deep_research_client:
            logger.info("ℹ️ Deep Research not available - using enhanced context analysis")
            return None
        
        try:
            # Aggregate topics and themes from articles
            themes = []
            context_data = []
            
            for article in processed_articles:
                # Extract themes from key points
                themes.extend(article.key_points)
                
                # Build context data
                context_data.append(f"""
                Title: {article.title}
                Source: {article.source}
                Key Points: {'; '.join(article.key_points)}
                Insights: {article.gemini_insights[:200]}...
                """)
            
            # Create comprehensive research query
            research_query = f"""
            Comprehensive Bitcoin Mining Industry Analysis for {datetime.now().strftime('%B %d, %Y')}
            
            Based on today's news coverage, provide deep research on:
            1. Current market trends and their implications for mining profitability
            2. Technical developments affecting mining efficiency and operations
            3. Regulatory landscape changes impacting mining businesses
            4. Economic factors influencing mining investment decisions
            5. Strategic recommendations for mining operations
            6. Risk assessment and mitigation strategies
            7. Future outlook and emerging opportunities
            
            Provide counter-arguments, alternative perspectives, and potential contrarian views.
            Focus on actionable insights for Bitcoin mining businesses and investors.
            Include specific implications for different types of mining operations (small-scale, industrial, renewable-focused).
            """
            
            logger.info("🔬 Initiating Deep Research analysis...")
            result = await self.deep_research_client.stream_assist(
                query=research_query,
                context_data=context_data
            )
            
            logger.info("✅ Deep Research completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Deep Research failed: {e}")
            return None
    
    def generate_daily_brief(self, 
                           processed_articles: List[ProcessedArticle], 
                           deep_research: Optional[DeepResearchResult] = None) -> str:
        """
        Generate comprehensive daily brief for Bitcoin miners.
        
        Args:
            processed_articles: List of AI-processed articles
            deep_research: Optional deep research results
            
        Returns:
            Formatted daily brief as markdown string
        """
        logger.info("📝 Generating comprehensive daily brief...")
        
        try:
            if not self.gemini_client:
                logger.warning("⚠️ Gemini client not available - generating basic brief")
                return self._generate_basic_brief(processed_articles, deep_research)
            
            # Prepare comprehensive context for brief generation
            articles_context = self._prepare_articles_context(processed_articles)
            deep_research_context = self._prepare_deep_research_context(deep_research)
            
            brief_prompt = f"""
            Create a comprehensive Daily Bitcoin Mining Brief for {datetime.now().strftime('%B %d, %Y')}.
            
            This brief is for BITCOIN MINERS - focus on practical implications for mining operations,
            profitability, efficiency, regulatory compliance, and strategic decisions.
            
            ARTICLE SUMMARIES:
            {articles_context}
            
            DEEP RESEARCH INSIGHTS:
            {deep_research_context}
            
            REQUIREMENTS:
            1. Professional formatting with clear headings and structure
            2. Executive Summary highlighting key takeaways for miners
            3. Detailed analysis linking all news together with fresh perspective
            4. Counter-arguments and alternative viewpoints where applicable
            5. Strategic recommendations for mining operations
            6. Risk assessment and mitigation strategies  
            7. Future implications and opportunities
            8. Actionable insights for different mining scales (small, medium, industrial)
            
            FORMAT as structured markdown with:
            - Executive Summary
            - Market Analysis  
            - Technical Developments
            - Regulatory & Compliance Updates
            - Economic Factors & Profitability
            - Strategic Recommendations
            - Risk Assessment
            - Future Outlook
            - Key Takeaways for Miners
            
            Ensure ALL articles are referenced and integrated into a cohesive narrative.
            Include specific numbers, dates, and concrete implications when available.
            Provide contrarian views and potential alternative interpretations.
            """
            
            response = self.gemini_client.model.generate_content(brief_prompt)
            brief_content = response.text.strip()
            
            # Add metadata header
            metadata_header = f"""# Bitcoin Mining Daily Brief
**Date:** {datetime.now().strftime('%B %d, %Y')}  
**Articles Analyzed:** {len(processed_articles)}  
**Deep Research:** {'✅ Enabled' if deep_research else '❌ Not Available'}  
**Generated:** {datetime.now().strftime('%I:%M %p UTC')}  

---

"""
            
            return metadata_header + brief_content
            
        except Exception as e:
            logger.error(f"❌ Error generating daily brief: {e}")
            return self._generate_basic_brief(processed_articles, deep_research)
    
    def _prepare_articles_context(self, processed_articles: List[ProcessedArticle]) -> str:
        """Prepare article context for brief generation."""
        context_parts = []
        
        for i, article in enumerate(processed_articles, 1):
            context_parts.append(f"""
            Article {i}: {article.title}
            Source: {article.source}
            Relevance Score: {article.mining_relevance_score:.1f}/1.0
            Summary: {article.summary}
            Key Points: {'; '.join(article.key_points)}
            Mining Insights: {article.gemini_insights}
            URL: {article.url}
            """)
        
        return "\n".join(context_parts)
    
    def _prepare_deep_research_context(self, deep_research: Optional[DeepResearchResult]) -> str:
        """Prepare deep research context for brief generation."""
        if not deep_research:
            return "Deep Research not available - using article-based analysis only."
        
        return f"""
        Research Query: {deep_research.query}
        Summary: {deep_research.research_summary}
        Key Findings: {'; '.join(deep_research.key_findings)}
        Confidence Score: {deep_research.confidence_score:.2f}
        Sources: {', '.join(deep_research.sources)}
        """
    
    def _generate_basic_brief(self, 
                            processed_articles: List[ProcessedArticle], 
                            deep_research: Optional[DeepResearchResult] = None) -> str:
        """Generate basic brief without AI enhancement."""
        current_date = datetime.now().strftime('%B %d, %Y')
        
        brief = f"""# Bitcoin Mining Daily Brief
**Date:** {current_date}  
**Articles Analyzed:** {len(processed_articles)}  
**Deep Research:** {'✅ Enabled' if deep_research else '❌ Not Available'}  
**Generated:** {datetime.now().strftime('%I:%M %p UTC')}  

---

## Executive Summary

Today's Bitcoin mining news covers {len(processed_articles)} significant developments affecting the industry. Key areas of focus include market dynamics, technical developments, and regulatory considerations impacting mining operations.

## Article Summaries

"""
        
        for i, article in enumerate(processed_articles, 1):
            brief += f"""### {i}. {article.title}
**Source:** {article.source}  
**Relevance:** {article.mining_relevance_score:.1f}/1.0  
**Published:** {article.published_date}  

**Summary:** {article.summary}

**Key Points for Miners:**
{chr(10).join(f'• {point}' for point in article.key_points)}

**Strategic Insights:** {article.gemini_insights}

**Read More:** [{article.url}]({article.url})

---

"""
        
        if deep_research:
            brief += f"""## Deep Research Analysis

**Research Focus:** {deep_research.query}

**Key Findings:**
{chr(10).join(f'• {finding}' for finding in deep_research.key_findings)}

**Summary:** {deep_research.research_summary}

---

"""
        
        brief += """## Key Takeaways for Miners

• Monitor market developments for profitability implications
• Stay informed about regulatory changes affecting operations  
• Evaluate technical developments for efficiency opportunities
• Consider economic factors in investment and scaling decisions
• Maintain strategic flexibility in rapidly evolving landscape

---

*This brief was generated using advanced AI analysis. For critical business decisions, please consult additional sources and professional advisors.*
"""
        
        return brief
    
    def save_brief(self, brief_content: str, filename: Optional[str] = None) -> str:
        """
        Save the daily brief to a file.
        
        Args:
            brief_content: The generated brief content
            filename: Optional custom filename
            
        Returns:
            Path to the saved file
        """
        try:
            if not filename:
                date_str = datetime.now().strftime('%Y-%m-%d')
                filename = f"bitcoin_mining_brief_{date_str}.md"
            
            file_path = Path(filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(brief_content)
            
            logger.info(f"✅ Daily brief saved to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Error saving brief: {e}")
            return ""
    
    async def generate_complete_brief(self) -> str:
        """
        Generate complete daily brief with all processing steps.
        
        Returns:
            Complete daily brief as formatted string
        """
        logger.info("🚀 Starting complete daily brief generation...")
        
        try:
            # Step 1: Fetch all daily articles
            daily_articles = self.fetch_daily_articles(days_ago=1)
            
            if not daily_articles:
                logger.warning("⚠️ No articles found for daily brief")
                return self._generate_no_articles_brief()
            
            logger.info(f"📰 Processing {len(daily_articles)} articles...")
            
            # Step 2: Process articles with Gemini AI
            processed_articles = []
            for article_data in daily_articles:
                try:
                    processed_article = self.process_article_with_gemini(article_data)
                    processed_articles.append(processed_article)
                except Exception as e:
                    logger.error(f"❌ Error processing article: {e}")
                    # Continue with other articles
            
            logger.info(f"✅ Successfully processed {len(processed_articles)} articles")
            
            # Step 3: Perform deep research (if available)
            deep_research_result = None
            if self.deep_research_client:
                try:
                    deep_research_result = await self.perform_deep_research(processed_articles)
                except Exception as e:
                    logger.error(f"❌ Deep research failed: {e}")
            
            # Step 4: Generate comprehensive brief
            brief_content = self.generate_daily_brief(processed_articles, deep_research_result)
            
            # Step 5: Save brief
            saved_path = self.save_brief(brief_content)
            
            logger.info("✅ Daily brief generation completed successfully")
            return brief_content
            
        except Exception as e:
            logger.error(f"❌ Complete brief generation failed: {e}")
            return self._generate_error_brief(str(e))
    
    def _generate_no_articles_brief(self) -> str:
        """Generate brief when no articles are available."""
        current_date = datetime.now().strftime('%B %d, %Y')
        return f"""# Bitcoin Mining Daily Brief
**Date:** {current_date}  
**Articles Analyzed:** 0  
**Status:** No Recent Articles Found  
**Generated:** {datetime.now().strftime('%I:%M %p UTC')}  

---

## Summary

No Bitcoin mining articles were found in the last 24 hours. This could indicate:

• Quiet news day for the mining industry
• All recent articles have already been processed
• Potential issues with article fetching systems

## Recommendations

• Check back later for updated content
• Review previous briefs for ongoing developments
• Monitor industry sources directly for breaking news

---

*Brief generation system is operational - waiting for new content.*
"""
    
    def _generate_error_brief(self, error_msg: str) -> str:
        """Generate brief when errors occur."""
        current_date = datetime.now().strftime('%B %d, %Y')
        return f"""# Bitcoin Mining Daily Brief - Error Report
**Date:** {current_date}  
**Status:** ❌ Generation Failed  
**Generated:** {datetime.now().strftime('%I:%M %p UTC')}  

---

## Error Summary

Daily brief generation encountered an error:

```
{error_msg}
```

## Recommendations

• Check system logs for detailed error information
• Verify API key configurations
• Ensure all dependencies are properly installed
• Contact system administrator if issues persist

---

*Please resolve the error to restore daily brief functionality.*
"""


def main():
    """Main execution function for daily briefing generation."""
    import asyncio
    
    logger.info("🌅 Bitcoin Mining Daily Briefing Generator")
    logger.info("=" * 50)
    
    try:
        # Initialize the briefing generator
        briefing_generator = DailyBriefingGenerator()
        
        # Generate complete daily brief
        brief = asyncio.run(briefing_generator.generate_complete_brief())
        
        # Output the brief
        print("\n" + "=" * 80)
        print("DAILY BRIEF OUTPUT")
        print("=" * 80)
        print(brief)
        print("=" * 80)
        
        logger.info("🎉 Daily briefing completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Daily briefing interrupted by user")
    except Exception as e:
        logger.error(f"❌ Daily briefing failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()