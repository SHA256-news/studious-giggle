"""Gemini AI client utilities for the Bitcoin Mining News Bot."""

from __future__ import annotations

import logging
from datetime import datetime
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
        """Generate a tweet headline with 3 summary points using Gemini Thinking."""
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

            # Extract the tweet text from the response
            tweet_text = response.text.strip()
            
            # Validate character count
            if len(tweet_text) > 280:
                logger.warning(f"Generated tweet headline exceeds 280 characters ({len(tweet_text)}), truncating...")
                tweet_text = tweet_text[:277] + "..."
            
            logger.info(f"Generated tweet headline ({len(tweet_text)} chars): {tweet_text[:100]}...")
            return tweet_text

        except Exception as exc:
            logger.error(f"Failed to generate tweet headline: {exc}")
            # Fallback to original title with truncation
            fallback = title[:277] + "..." if len(title) > 277 else title
            return fallback

    def _create_tweet_headline_prompt(self, title: str, body: str, url: str) -> str:
        """Create prompt for generating tweet headlines with 3 summary points."""
        trimmed_body = body[:3000]
        prompt = f"""
You are a Bitcoin mining news expert creating engaging Twitter content.

Using the source article provided, create a single tweet that includes:
1. A relevant, engaging headline 
2. Three concise bullet points summarizing the key aspects of the article
3. The entire tweet must be exactly 280 characters or less

Format your response as plain text ready to post on Twitter. Use bullet points (•) for the three summary points.

Requirements:
- Start with an engaging headline that captures the essence of the news
- Follow with exactly 3 bullet points using • symbol
- Keep it informative but concise for Twitter audience
- Focus on Bitcoin mining impact, financial figures, and key developments
- Must fit within 280 character limit total

Source Article Title: {title}
Source Article URL: {url}
Source Article Content: {trimmed_body}

Generate the tweet now:
"""
        return prompt

