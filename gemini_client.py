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
            if len(headline) > 150:  # Leave room for summary
                logger.warning(f"Generated headline exceeds 150 characters ({len(headline)}), truncating...")
                headline = headline[:147] + "..."
            
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
            if len(summary) > 120:  # Leave room for headline
                logger.warning(f"Generated summary exceeds 120 characters ({len(summary)}), truncating...")
                summary = summary[:117] + "..."
            
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

Using the source article provided, create a catchy, engaging headline for a tweet:

Requirements:
- Create a compelling headline that captures the essence of the news
- Make it attention-grabbing and informative
- Keep it under 150 characters to leave room for additional content
- Focus on Bitcoin mining impact, financial figures, and key developments
- Use emojis sparingly and appropriately
- Do NOT include bullet points or additional summary content

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

Using the source article provided, create exactly 3 concise bullet points that summarize the key aspects:

Requirements:
- Create exactly 3 bullet points using • symbol
- Each point should be very concise (under 40 characters each)
- Focus on Bitcoin mining impact, financial figures, and key developments
- Keep it informative but brief for Twitter audience
- Total summary should be under 120 characters
- Do NOT include a headline or additional content

Source Article Title: {title}
Source Article URL: {url}
Source Article Content: {trimmed_body}

Generate only the 3 bullet points now:
"""
        return prompt

