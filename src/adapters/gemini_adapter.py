"""
Gemini adapter - generates AI-powered headlines and summaries.
"""
import logging
from typing import Optional

from google import genai

from src.domain import Article
from src.adapters.interfaces import AIProvider, AIProviderError

logger = logging.getLogger(__name__)


class GeminiAdapter(AIProvider):
    """Adapter for Google Gemini AI."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key
            model: Model name to use
        """
        if not api_key:
            raise ValueError("Gemini API key cannot be empty")
        
        self.api_key = api_key
        self.model = model
        self._client: Optional[genai.Client] = None
    
    @property
    def client(self) -> genai.Client:
        """Lazy-load Gemini client."""
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        try:
            # Simple availability check
            return self._client is not None or bool(self.api_key)
        except Exception:
            return False
    
    def generate_headline(
        self,
        article: Article,
        max_length: int = 80
    ) -> Optional[str]:
        """
        Generate a professional headline for the article.
        
        Args:
            article: Article to generate headline for
            max_length: Maximum character length
            
        Returns:
            Generated headline or None if generation fails
        """
        try:
            prompt = self._build_headline_prompt(article, max_length)
            
            config = {
                "tools": [{"url_context": {}}]  # Enable URL context
            }
            
            logger.info(f"Generating headline for: {article.url}")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            
            # Check for URL retrieval errors
            self._check_url_errors(response, article.url)
            
            # Extract and clean headline
            headline = response.text.strip()
            headline = self._clean_headline(headline)
            
            if len(headline) > max_length:
                headline = headline[:max_length - 3] + "..."
            
            logger.info(f"Generated headline ({len(headline)} chars): {headline}")
            return headline
            
        except Exception as e:
            logger.error(f"Failed to generate headline: {e}")
            return None
    
    def generate_summary(
        self,
        article: Article,
        headline: str,
        max_length: int = 180
    ) -> Optional[str]:
        """
        Generate a summary that complements the headline.
        
        Args:
            article: Article to summarize
            headline: Previously generated headline
            max_length: Maximum character length
            
        Returns:
            Generated summary or None if generation fails
        """
        try:
            prompt = self._build_summary_prompt(article, headline, max_length)
            
            config = {
                "tools": [{"url_context": {}}]
            }
            
            logger.info(f"Generating summary for: {article.url}")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            
            # Check for URL retrieval errors
            self._check_url_errors(response, article.url)
            
            # Extract and clean summary
            summary = response.text.strip()
            summary = self._clean_summary(summary)
            
            if len(summary) > max_length:
                summary = summary[:max_length - 3] + "..."
            
            logger.info(f"Generated summary ({len(summary)} chars)")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return None
    
    def _build_headline_prompt(self, article: Article, max_length: int) -> str:
        """Build prompt for headline generation."""
        return f"""You are a professional Bitcoin mining news headline writer.

Read this article: {article.url}

Write ONE concise, professional headline ({max_length} chars max) that:
- Captures the main newsworthy point
- Uses active voice and specific facts
- Avoids phrases like "The article states" or "According to the article"
- Follows Bloomberg/Reuters style

Examples of GOOD headlines:
- "Marathon Digital Deploys 5,000 S19 XP Miners in West Texas"
- "Bitcoin Mining Difficulty Hits All-Time High at 62.5T"
- "JPMorgan Downgrades CleanSpark Stock to Neutral"

Examples of BAD headlines:
- "The article discusses how Marathon Digital is expanding"
- "New report shows Bitcoin mining difficulty increased"

Just output the headline - no preamble, quotes, or explanation."""
    
    def _build_summary_prompt(
        self,
        article: Article,
        headline: str,
        max_length: int
    ) -> str:
        """Build prompt for summary generation."""
        return f"""You are a professional Bitcoin mining news summarizer.

Read this article: {article.url}

The headline is already written: "{headline}"

Write a SHORT bullet-point summary ({max_length} chars max) with ADDITIONAL details not in the headline:
- Use 2-4 bullet points with line breaks
- Each point: one specific fact, number, or development
- NO repetition of headline information
- NO generic statements or preamble

Example format:
• Deployment starts Q2 2024
• 8-month ROI target
• Powered by 100MW facility

Just output the bullet points - nothing else."""
    
    def _check_url_errors(self, response, url: str) -> None:
        """
        Check if URL retrieval failed.
        
        Args:
            response: Gemini API response
            url: Article URL
            
        Raises:
            AIProviderError: If URL retrieval failed
        """
        # Check response metadata for URL retrieval status
        if hasattr(response, 'url_context_metadata'):
            metadata = response.url_context_metadata
            if metadata and hasattr(metadata, 'url_retrieval_status'):
                status = str(metadata.url_retrieval_status)
                if "ERROR" in status or "FAILED" in status:
                    raise AIProviderError(f"Failed to retrieve URL content: {url}")
        
        # Check response text for error indicators
        response_text = response.text.lower()
        error_phrases = [
            "unable to fetch",
            "unable to access",
            "cannot access",
            "failed to retrieve",
            "not accessible"
        ]
        
        if any(phrase in response_text for phrase in error_phrases):
            raise AIProviderError(f"URL content not accessible: {url}")
    
    def _clean_headline(self, text: str) -> str:
        """Clean and normalize headline text."""
        # Remove quotes if present
        text = text.strip('"\'')
        
        # Remove common unwanted prefixes
        prefixes = [
            "headline:",
            "here's the headline:",
            "title:",
        ]
        
        text_lower = text.lower()
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Ensure first letter is capitalized
        if text:
            text = text[0].upper() + text[1:]
        
        return text
    
    def _clean_summary(self, text: str) -> str:
        """Clean and normalize summary text."""
        # Remove common unwanted prefixes
        prefixes = [
            "summary:",
            "here's the summary:",
            "here are the key points:",
        ]
        
        text_lower = text.lower()
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                text = text[len(prefix):].strip()
        
        return text
