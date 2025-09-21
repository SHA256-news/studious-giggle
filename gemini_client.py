"""Gemini AI client utilities for the Bitcoin Mining News Bot."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from config import GeminiConfig

logger = logging.getLogger('bitcoin_mining_bot')


def create_filename_slug(title: str) -> str:
    """Create a filesystem-safe slug derived from a title string."""
    import re

    slug = re.sub(r'[^\w\s-]', '', (title or '').lower())
    slug = re.sub(r'[-\s]+', '_', slug)
    return slug[:50]


class GeminiClient:
    """Wrapper for Google Gemini AI client using the google-genai SDK."""

    def __init__(self, config: GeminiConfig):
        """Initialize Gemini client."""
        # The new SDK automatically picks up GEMINI_API_KEY from environment
        self.client = genai.Client()
        logger.info("Gemini AI client initialized successfully with new SDK")

    def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a news article using Gemini AI."""
        try:
            title = article.get('title', 'No title')
            body = article.get('body', article.get('summary', 'No content'))
            url = article.get('url', article.get('uri', 'No URL'))

            prompt = self._create_analysis_prompt(title, body, url)

            logger.info(f"Analyzing article: {title[:50]}...")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                ),
            )

            analysis = {
                'article_title': title,
                'article_url': url,
                'analysis_text': response.text,
                'analysis_timestamp': datetime.now().isoformat(),
                'model_used': 'gemini-2.5-flash',
            }

            logger.info("Article analysis completed successfully")
            return analysis

        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error(f"Failed to analyze article: {exc}")
            return {
                'article_title': article.get('title', 'Unknown'),
                'article_url': article.get('url', article.get('uri', 'No URL')),
                'analysis_text': f"Analysis failed: {exc}",
                'analysis_timestamp': datetime.now().isoformat(),
                'model_used': 'gemini-2.5-flash',
                'error': True,
            }

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

    def generate_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a publishable article for the provided news item."""
        title = article.get('title', 'Untitled Article')
        summary = article.get('body', article.get('summary', ''))
        url = article.get('url', article.get('uri', ''))

        prompt = self._create_article_prompt(title, summary, url)

        try:
            logger.info(f"Generating long-form article: {title[:50]}...")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                ),
            )

            structured_article = self._parse_article_response(
                response.text,
                fallback_headline=title,
                fallback_subhead=article.get('summary', '')
                or 'Insights on the latest Bitcoin mining developments',
            )

            structured_article.update(
                {
                    'source_title': title,
                    'source_url': url,
                    'generated_timestamp': datetime.now().isoformat(),
                    'model_used': 'gemini-2.5-flash',
                }
            )

            logger.info("Article generation completed successfully")
            return structured_article

        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error(f"Failed to generate article: {exc}")
            return {
                'headline': title,
                'subhead': 'Failed to generate article',
                'sections': [
                    {
                        'title': 'Generation Error',
                        'content': f"The article could not be generated due to: {exc}",
                    }
                ],
                'source_title': title,
                'source_url': url,
                'generated_timestamp': datetime.now().isoformat(),
                'model_used': 'gemini-2.5-flash',
                'error': True,
            }

    def _create_analysis_prompt(self, title: str, body: str, url: str) -> str:
        """Create a detailed analysis prompt for the article."""
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

    def _create_article_prompt(self, title: str, body: str, url: str) -> str:
        """Create prompt that requests a fully publishable article."""
        trimmed_body = body[:4000]
        prompt = f"""
You are a financial journalist focused on Bitcoin mining.

Using the information provided, write a publishable news article that follows this JSON schema:

{{
  "headline": "Compelling headline",
  "subhead": "One sentence subhead providing context",
  "sections": [
    {{"title": "Section heading", "content": "2-3 paragraphs expanding on the topic"}}
  ]
}}

Guidelines:
- Maintain journalistic neutrality and cite concrete facts from the source material.
- Include at least three body sections covering background, impact on Bitcoin mining, and market or regulatory implications.
- Avoid Markdown formatting in the JSON values; provide plain text paragraphs.

Source Article Title: {title}
Source Article URL: {url}
Source Article Content:
"""
        return prompt + trimmed_body

    def _parse_article_response(
        self,
        response_text: str,
        fallback_headline: str,
        fallback_subhead: str,
    ) -> Dict[str, Any]:
        """Parse Gemini response text into a structured article object."""

        def _normalize_sections(sections: Any) -> List[Dict[str, str]]:
            normalized: List[Dict[str, str]] = []
            if isinstance(sections, list):
                for index, section in enumerate(sections, start=1):
                    if isinstance(section, dict):
                        title = section.get('title') or section.get('heading') or f'Section {index}'
                        content = section.get('content') or section.get('body', '')
                    else:
                        title = f'Section {index}'
                        content = str(section)
                    normalized.append({'title': title.strip(), 'content': content.strip()})
            return [item for item in normalized if item['content']]

        try:
            data = json.loads(response_text)
            headline = (data.get('headline') or fallback_headline).strip()
            subhead = (data.get('subhead') or fallback_subhead).strip()
            sections = _normalize_sections(data.get('sections', []))
        except (json.JSONDecodeError, AttributeError):
            logger.debug("Gemini article response was not valid JSON; using fallback structure")
            headline = fallback_headline
            subhead = fallback_subhead
            sections = _normalize_sections([])

        if not sections:
            sections = [
                {
                    'title': 'Key Developments',
                    'content': response_text.strip(),
                }
            ]

        return {
            'headline': headline,
            'subhead': subhead,
            'sections': sections,
            'raw_text': response_text,
        }


class ReportGenerator:
    """Generates and saves markdown reports for analyzed articles."""

    def __init__(self, reports_dir: str = "docs/reports"):
        self.reports_dir = reports_dir
        self._ensure_reports_directory()

    def _ensure_reports_directory(self) -> None:
        os.makedirs(self.reports_dir, exist_ok=True)
        logger.info(f"Reports directory ensured: {self.reports_dir}")

    def save_analysis_report(self, analysis: Dict[str, Any]) -> Optional[str]:
        """Save analysis report as markdown file."""
        try:
            created_at = datetime.now()
            timestamp = created_at.strftime("%Y%m%d_%H%M%S")
            permalink_timestamp = created_at.strftime("%Y%m%d-%H%M%S")
            title_slug = self._create_filename_slug(analysis['article_title']) or "report"
            filename = f"{timestamp}_{title_slug}.md"
            filepath = os.path.join(self.reports_dir, filename)

            markdown_content = self._generate_markdown_report(
                analysis,
                slug=title_slug,
                permalink=f"/reports/{permalink_timestamp}-{title_slug}/",
                generated_at=created_at.isoformat(),
            )

            with open(filepath, 'w', encoding='utf-8') as handle:
                handle.write(markdown_content)

            logger.info(f"Analysis report saved: {filepath}")
            return filepath

        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error(f"Failed to save analysis report: {exc}")
            return None

    def _create_filename_slug(self, title: str) -> str:
        return create_filename_slug(title)

    def _generate_markdown_report(
        self,
        analysis: Dict[str, Any],
        *,
        slug: str,
        permalink: str,
        generated_at: str,
    ) -> str:
        timestamp = analysis.get('analysis_timestamp', datetime.now().isoformat())
        model = analysis.get('model_used', 'Unknown')

        front_matter: Dict[str, Any] = {
            'layout': 'report',
            'title': f"Analysis: {analysis['article_title']}",
            'slug': slug,
            'permalink': permalink,
            'source_url': analysis.get('article_url'),
            'article_title': analysis.get('article_title'),
            'generated_at': generated_at,
            'analysis_date': timestamp,
            'model_used': model,
        }

        lines: List[str] = [ArticleContentManager._render_front_matter(front_matter)]
        lines.extend(
            [
                "# Bitcoin Mining News Analysis Report",
                "",
                "## Article Information",
                f"- **Title**: {analysis['article_title']}",
                f"- **URL**: {analysis['article_url']}",
                f"- **Analysis Date**: {timestamp}",
                f"- **AI Model**: {model}",
                "",
                "---",
                "",
                "## AI Analysis",
                "",
                analysis['analysis_text'],
                "",
                "---",
                "",
                "*This report was automatically generated by the Bitcoin Mining News Bot using AI analysis.*",
            ]
        )
        return "\n".join(lines).strip() + "\n"


class ArticleContentManager:
    """Persist structured articles generated by Gemini into the static site."""

    def __init__(self, content_dir: str = "docs/articles"):
        self.content_dir = content_dir
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        os.makedirs(self.content_dir, exist_ok=True)
        logger.info(f"Article content directory ensured: {self.content_dir}")

    def save_article(self, article: Dict[str, Any], source_article: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Save the structured article to disk as markdown."""
        headline = article.get('headline') or (source_article or {}).get('title') or 'Bitcoin Mining Article'
        created_at = datetime.now()
        timestamp = created_at.strftime("%Y%m%d_%H%M%S")
        permalink_timestamp = created_at.strftime("%Y%m%d-%H%M%S")
        slug = create_filename_slug(headline) or "article"
        filename = f"{timestamp}_{slug}.md"
        filepath = os.path.join(self.content_dir, filename)

        markdown_content = self._render_article(
            article,
            source_article,
            slug=slug,
            permalink=f"/articles/{permalink_timestamp}-{slug}/",
            generated_at=created_at.isoformat(),
        )

        try:
            with open(filepath, 'w', encoding='utf-8') as handle:
                handle.write(markdown_content)
            logger.info(f"Article saved to {filepath}")
            return filepath
        except OSError as exc:  # pragma: no cover - file system edge case
            logger.error(f"Failed to save article content: {exc}")
            return None

    def _render_article(
        self,
        article: Dict[str, Any],
        source_article: Optional[Dict[str, Any]] = None,
        *,
        slug: str,
        permalink: str,
        generated_at: str,
    ) -> str:
        """Render the structured article as markdown content with Jekyll front matter."""
        headline = article.get('headline', 'Bitcoin Mining Article')
        subhead = article.get('subhead', '')
        sections: List[Dict[str, str]] = article.get('sections', [])
        source_url = (source_article or {}).get('url', (source_article or {}).get('uri'))

        front_matter: Dict[str, Any] = {
            'layout': 'article',
            'title': headline.strip(),
            'description': (subhead or '').strip() or None,
            'slug': slug,
            'permalink': permalink,
            'source_url': source_url,
            'source_title': (source_article or {}).get('title'),
            'generated_at': article.get('generated_timestamp', generated_at),
            'model_used': article.get('model_used'),
        }

        lines: List[str] = [self._render_front_matter(front_matter)]
        lines.extend([f"# {headline.strip()}", ""])

        if subhead:
            lines.extend([f"## {subhead.strip()}", ""])

        for section in sections:
            title = section.get('title', '').strip() or 'Section'
            content = section.get('content', '').strip()
            if not content:
                continue
            lines.extend([f"### {title}", "", content, ""])

        if source_article:
            lines.extend([
                "---",
                "",
                "## Source Information",
                "",
                f"- Original Title: {source_article.get('title', 'Unknown')}",
                f"- Source URL: {source_article.get('url', source_article.get('uri', 'Unknown'))}",
            ])

        return "\n".join(lines).strip() + "\n"

    @staticmethod
    def _render_front_matter(metadata: Dict[str, Any]) -> str:
        """Render YAML-compatible front matter from metadata."""
        lines = ["---"]
        for key, value in metadata.items():
            if value in (None, ""):
                continue
            if isinstance(value, (list, dict)):
                lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
            else:
                lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        lines.append("---")
        lines.append("")
        return "\n".join(lines)
