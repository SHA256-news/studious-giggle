"""Gemini AI client utilities for the Bitcoin Mining News Bot with URL context support."""

from __future__ import annotations

import logging
from typing import Any, Dict

from google import genai
from google.genai import types

from config import GeminiConfig

logger = logging.getLogger('bitcoin_mining_bot')


class GeminiClient:
    """Wrapper for Google Gemini AI client using the google-genai SDK with URL context support."""

    def __init__(self, config: GeminiConfig):
        """Initialize Gemini client."""
        # The new SDK automatically picks up GEMINI_API_KEY from environment
        self.client = genai.Client()
        logger.info("Gemini AI client initialized successfully with new SDK")

    def generate_tweet_headline(self, article: Dict[str, Any]) -> str:
        """Generate a tweet headline using Gemini with URL context."""
        title = article.get('title', 'Untitled Article')
        body = article.get('body', article.get('summary', ''))
        url = article.get('url', article.get('uri', ''))

        prompt = self._create_tweet_headline_prompt(title, body, url)

        try:
            logger.info(f"Generating tweet headline with URL context: {title[:50]}...")
            
            # Configure tools to include URL context for better analysis
            tools = [{"url_context": {}}]
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=tools
                ),
            )

            # Extract the headline from the response
            headline = response.text.strip()
            
            # Clean up any debugging content that might have leaked through
            headline = self._clean_response_text(headline)
            
            # If headline was completely filtered out (all debugging), use fallback
            if not headline:
                logger.warning("Gemini headline was entirely debugging content, using title fallback")
                headline = title[:140] if title else "Bitcoin mining news"
            
            # Log URL context metadata if available
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'url_context_metadata') and candidate.url_context_metadata:
                    logger.info(f"URL context used for headline generation: {len(candidate.url_context_metadata.url_metadata) if candidate.url_context_metadata.url_metadata else 0} URLs retrieved")
            
            # Validate character count for headline only
            if len(headline) > 140:  # Leave room for summary
                logger.warning(f"Generated headline exceeds 140 characters ({len(headline)}), truncating...")
                headline = headline[:137] + "..."
            
            logger.info(f"Generated tweet headline ({len(headline)} chars): {headline[:100]}...")
            return headline

        except Exception as exc:
            logger.error(f"Failed to generate tweet headline with URL context: {exc}")
            # Fallback to original title with truncation
            fallback = title[:147] + "..." if len(title) > 147 else title
            return fallback

    def generate_tweet_summary(self, article: Dict[str, Any]) -> str:
        """Generate a 3-point summary for the tweet content using URL context."""
        title = article.get('title', 'Untitled Article')
        body = article.get('body', article.get('summary', ''))
        url = article.get('url', article.get('uri', ''))

        prompt = self._create_tweet_summary_prompt(title, body, url)

        try:
            logger.info(f"Generating tweet summary with URL context: {title[:50]}...")
            
            # Configure tools to include URL context for better analysis
            tools = [{"url_context": {}}]
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=tools
                ),
            )

            # Extract the summary from the response
            summary = response.text.strip()
            
            # Clean up any debugging content that might have leaked through
            summary = self._clean_response_text(summary)
            
            # If summary was completely filtered out (all debugging), use fallback
            if not summary:
                logger.warning("Gemini summary was entirely debugging content, using simple fallback")
                summary = "• Key development • Impact on mining • Market implications"
            
            # Log URL context metadata if available
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'url_context_metadata') and candidate.url_context_metadata:
                    logger.info(f"URL context used for summary generation: {len(candidate.url_context_metadata.url_metadata) if candidate.url_context_metadata.url_metadata else 0} URLs retrieved")
            
            # Validate character count for summary
            if len(summary) > 110:  # Leave room for headline
                logger.warning(f"Generated summary exceeds 110 characters ({len(summary)}), truncating...")
                summary = summary[:107] + "..."
            
            logger.info(f"Generated tweet summary ({len(summary)} chars): {summary[:50]}...")
            return summary

        except Exception as exc:
            logger.error(f"Failed to generate tweet summary with URL context: {exc}")
            # Fallback to a simple summary
            return "• Key development • Impact on mining • Market implications"

    def _create_tweet_headline_prompt(self, title: str, body: str, url: str) -> str:
        """Create prompt for generating engaging tweet headlines with URL context."""
        trimmed_body = body[:3000]
        prompt = f"""
You are a Bitcoin mining news expert creating engaging Twitter content.

Using the source article provided and the full content from the URL, create a catchy, engaging headline for a tweet that accurately represents the news.

Requirements:
- Create a compelling headline that captures the essence of the news
- Make it attention-grabbing and informative
- Keep it under 140 characters to leave room for additional content
- Focus on Bitcoin mining impact, financial figures, and key developments
- Use clear, professional language with proper grammar
- For business news: highlight company actions, investments, expansions
- For regulatory news: highlight policy changes, approvals, restrictions
- For scandal/crime news: be factual but not sensational
- Do NOT include bullet points, summaries, or additional content
- Do NOT use excessive emojis (maximum 1-2 if appropriate)
- Leverage the actual article content from the URL for accuracy and depth
- IMPORTANT: Return ONLY the headline text, no explanation or analysis

Source Article Title: {title}
Source Article URL: {url}
Source Article Summary: {trimmed_body}

Generate only the headline now:
"""
        return prompt

    def _create_tweet_summary_prompt(self, title: str, body: str, url: str) -> str:
        """Create prompt for generating 3-point summaries with URL context."""
        trimmed_body = body[:3000]
        prompt = f"""
You are a Bitcoin mining news expert creating engaging Twitter content.

Using the source article provided and the full content from the URL, create exactly 3 concise bullet points that summarize the key aspects of this Bitcoin mining news:

Requirements:
- Create exactly 3 bullet points using • symbol
- Each point should be very concise (under 35 characters each)
- Focus on the most important aspects: financial impact, technical details, market implications
- Use professional, clear language
- Total summary should be under 110 characters including bullet points
- Do NOT include a headline, introduction, or additional content
- Leverage the actual article content from the URL for accuracy and depth
- IMPORTANT: Return ONLY the 3 bullet points, no explanation or analysis
- Examples of good bullet points:
  • $50M investment announced
  • 2,200 mining rigs deployed  
  • Operations in Texas facility

Source Article Title: {title}
Source Article URL: {url}
Source Article Summary: {trimmed_body}

Generate only the 3 bullet points now:
"""
        return prompt

    def _clean_response_text(self, text: str) -> str:
        """Clean up Gemini response text to remove any debugging content and generic openings."""
        if not text:
            return text
            
        # Remove common debugging phrases that Gemini might output
        debugging_phrases = [
            "The article content was provided in the prompt, so",
            "Let's analyze the provided source",
            "I will use that",
            "Based on the article content",
            "Looking at the source article",
            "From the provided information",
            "Analyzing the article",
            "Here's the",
            "Here are the",
            "Based on the URL content",
            "Let me analyze"
        ]
        
        # Generic opening phrases to remove or replace
        generic_openings = [
            "The article states that ",
            "The article mentions that ",
            "According to the article, ",
            "The report states that ",
            "The news states that ",
            "It is reported that ",
            "The article discusses how ",
            "The piece explains that "
        ]
        
        # Remove lines that start with debugging phrases
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines that contain debugging phrases
            is_debugging = False
            for phrase in debugging_phrases:
                if phrase.lower() in line.lower():
                    is_debugging = True
                    logger.warning(f"Filtering out debugging text: {line[:50]}...")
                    break
                    
            if not is_debugging:
                clean_lines.append(line)
        
        # Join back and get the result
        result = '\n'.join(clean_lines).strip()
        
        # Remove generic openings from the final result
        for opening in generic_openings:
            if result.lower().startswith(opening.lower()):
                result = result[len(opening):].strip()
                # Capitalize the first letter after removing the opening
                if result:
                    result = result[0].upper() + result[1:] if len(result) > 1 else result.upper()
                logger.info(f"Removed generic opening: '{opening}'")
                break
        
        return result
        result = '\n'.join(clean_lines).strip()
        
        # If we filtered everything out, return a safe fallback instead of problematic original
        if not result and text:
            logger.warning("All text was filtered as debugging content, using fallback")
            # Return a safe fallback instead of the problematic debugging text
            return ""  # Let the calling function handle the empty response with its own fallback
            
        return result

