"""Gemini AI client utilities for the Bitcoin Mining News Bot."""

from __future__ import annotations

import logging
from typing import Any, Dict

from google import genai
from google.genai import types

from config import GeminiConfig

logger = logging.getLogger('bitcoin_mining_bot')


class GeminiClient:
    """Wrapper for Google Gemini AI client using the google-genai SDK."""

    def __init__(self, config: GeminiConfig):
        """Initialize Gemini client."""
        # The new SDK automatically picks up GEMINI_API_KEY from environment
        self.client = genai.Client()
        logger.info("Gemini AI client initialized successfully with new SDK")

    def generate_tweet_headline(self, article: Dict[str, Any]) -> str:
        """Generate a tweet headline using Gemini Thinking."""
        title = article.get('title', 'Untitled Article')
        body = article.get('body', article.get('summary', ''))
        url = article.get('url', article.get('uri', ''))

        prompt = self._create_tweet_headline_prompt(title, body, url)

        try:
            logger.info(f"Generating tweet headline: {title[:50]}...")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=10000)
                ),
            )

            # Extract the headline from the response
            headline = response.text.strip()
            
            # Validate character count for headline only
            if len(headline) > 140:  # Leave room for summary
                logger.warning(f"Generated headline exceeds 140 characters ({len(headline)}), truncating...")
                headline = headline[:137] + "..."
            
            logger.info(f"Generated tweet headline ({len(headline)} chars): {headline[:100]}...")
            return headline

        except Exception as exc:
            logger.error(f"Failed to generate tweet headline: {exc}")
            # Fallback to original title with truncation
            fallback = title[:147] + "..." if len(title) > 147 else title
            return fallback

    def generate_tweet_summary(self, article: Dict[str, Any]) -> str:
        """Generate a 3-point summary for the tweet content."""
        title = article.get('title', 'Untitled Article')
        body = article.get('body', article.get('summary', ''))
        url = article.get('url', article.get('uri', ''))

        prompt = self._create_tweet_summary_prompt(title, body, url)

        try:
            logger.info(f"Generating tweet summary: {title[:50]}...")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=10000)
                ),
            )

            # Extract the summary from the response
            summary = response.text.strip()
            
            # Validate character count for summary
            if len(summary) > 110:  # Leave room for headline
                logger.warning(f"Generated summary exceeds 110 characters ({len(summary)}), truncating...")
                summary = summary[:107] + "..."
            
            logger.info(f"Generated tweet summary ({len(summary)} chars): {summary[:50]}...")
            return summary

        except Exception as exc:
            logger.error(f"Failed to generate tweet summary: {exc}")
            # Fallback to a simple summary
            return "• Key development • Impact on mining • Market implications"

    def _create_tweet_headline_prompt(self, title: str, body: str, url: str) -> str:
        """Create prompt for generating engaging tweet headlines."""
        trimmed_body = body[:3000]
        prompt = f"""
You are a Bitcoin mining news expert creating engaging Twitter content.

Using the source article provided, create a catchy, engaging headline for a tweet that accurately represents the news.

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

Source Article Title: {title}
Source Article URL: {url}
Source Article Content: {trimmed_body}

Generate only the headline now:
"""
        return prompt

    def _create_tweet_summary_prompt(self, title: str, body: str, url: str) -> str:
        """Create prompt for generating 3-point summaries."""
        trimmed_body = body[:3000]
        prompt = f"""
You are a Bitcoin mining news expert creating engaging Twitter content.

Using the source article provided, create exactly 3 concise bullet points that summarize the key aspects of this Bitcoin mining news:

Requirements:
- Create exactly 3 bullet points using • symbol
- Each point should be very concise (under 35 characters each)
- Focus on the most important aspects: financial impact, technical details, market implications
- Use professional, clear language
- Total summary should be under 110 characters including bullet points
- Do NOT include a headline, introduction, or additional content
- Examples of good bullet points:
  • $50M investment announced
  • 2,200 mining rigs deployed  
  • Operations in Texas facility

Source Article Title: {title}
Source Article URL: {url}
Source Article Content: {trimmed_body}

Generate only the 3 bullet points now:
"""
        return prompt

