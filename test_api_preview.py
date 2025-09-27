#!/usr/bin/env python3
"""
GitHub Actions API Testing Script
=================================
Tests EventRegistry and Gemini APIs and creates GitHub issue with thread previews.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core import BitcoinMiningBot, Config, TextProcessor
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_apis_and_create_issue():
    """Test APIs and generate GitHub issue content."""
    print('🧪 Testing Live APIs for Thread Preview')
    print('=' * 50)
    
    # Check if running in GitHub Actions
    is_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
    
    try:
        # Get max articles from environment or default to 3
        max_articles = int(os.environ.get('MAX_ARTICLES', '3'))
        
        # Initialize bot
        config = Config.from_env()
        missing_keys = config.validate()
        
        if 'EVENTREGISTRY_API_KEY' in missing_keys:
            print('❌ EventRegistry API key missing')
            if is_github_actions:
                create_error_issue("EventRegistry API key missing from GitHub secrets")
                return True  # Success in GitHub Actions - issue created
            else:
                print('💡 Set EVENTREGISTRY_API_KEY environment variable to test locally')
                return False  # Fail locally when keys missing
            
        bot = BitcoinMiningBot(config=config)
        
        # Fetch articles
        print(f'📰 Fetching up to {max_articles} articles from EventRegistry...')
        articles = bot.news.fetch_articles()[:max_articles]
        
        if not articles:
            print('❌ No articles found')
            if is_github_actions:
                create_no_articles_issue()
                return True  # Success in GitHub Actions - issue created
            else:
                print('💡 This can happen when no recent Bitcoin mining news is available')
                return False  # Fail locally when no articles
        
        print(f'✅ Found {len(articles)} articles')
        
        # Test Gemini availability
        gemini_available = 'GEMINI_API_KEY' not in missing_keys and bot.gemini is not None
        print(f'🤖 Gemini AI: {"Available" if gemini_available else "Not Available"}')
        
        # Generate thread previews
        create_preview_issue(articles, gemini_available, bot)
        
        print('✅ Preview generated successfully')
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        
        # Check if running in GitHub Actions (in except block)
        is_github_actions_error = os.environ.get('GITHUB_ACTIONS') == 'true'
        if is_github_actions_error:
            create_error_issue(f"API testing error: {str(e)}")
            return True  # Success in GitHub Actions - error issue created
        else:
            print('💡 Fix the error above and try again')
            return False  # Fail locally on errors


def create_preview_issue(articles, gemini_available, bot):
    """Create GitHub issue with thread previews."""
    issue_body = f'''# 🧵 Thread Previews - {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}

**API Status:**
- ✅ EventRegistry: {len(articles)} articles fetched
- {'✅' if gemini_available else '❌'} Gemini AI: {'Available' if gemini_available else 'Not Available'}

**Thread Previews:**

'''
    
    for i, article in enumerate(articles, 1):
        issue_body += f'''## 📰 Article {i}

**Title:** {article.title}
**Source:** {article.source or "Unknown"}
**Published:** {article.date_published}
**URL:** {article.url}

### 🧵 Generated Thread:

'''
        
        try:
            thread = TextProcessor.create_tweet_thread(article, bot.gemini if gemini_available else None)
            
            for j, tweet in enumerate(thread, 1):
                issue_body += f'''**Tweet {j}:** ({len(tweet)} chars)
```
{tweet}
```

'''
            
            issue_body += f'''**Thread Summary:** {len(thread)} tweets total

---

'''
        except Exception as e:
            issue_body += f'''❌ **Error generating thread:** {str(e)}

---

'''
    
    issue_body += '''## 📝 Next Steps

1. **Review the threads above** - Check quality of headlines and summaries
2. **Edit if needed** - Adjust Gemini prompts in `core.py` if threads need improvement  
3. **Test again** - Run this workflow again to see updated results
4. **Go live** - Let the main workflow run automatically when satisfied

## 🛠️ Editing Guidelines

**To improve thread quality:**
- Edit `GeminiClient.generate_catchy_headline()` in `core.py` for better headlines
- Edit `GeminiClient.generate_thread_summary()` in `core.py` for better summaries
- Adjust prompts to match your preferred style and tone

**Thread Structure:**
- With Gemini: Headline → Summary (3 points) → URL
- Without Gemini: Smart prefix + title → URL
'''
    
    save_issue_content(issue_body)


def create_no_articles_issue():
    """Create issue for no articles found."""
    issue_body = '''# ⚠️ No Articles Found

**EventRegistry API Response:** No Bitcoin mining articles found in the last 6 hours.

This could mean:
- No recent Bitcoin mining news
- API filters too restrictive  
- EventRegistry API issue

**Next Steps:**
1. Check EventRegistry dashboard for available articles
2. Review API filters in core.py
3. Try again later when fresh news is available
'''
    save_issue_content(issue_body)


def create_error_issue(error_msg):
    """Create issue for errors."""
    error_issue = f'''# ❌ API Testing Error

**Error occurred during API testing:**

```
{error_msg}
```

**Timestamp:** {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}

**Troubleshooting:**
1. Check API key configuration in GitHub secrets
2. Verify EventRegistry API quota/status
3. Check Gemini API availability
4. Review error logs above for specific issues

**Next Steps:**
- Fix the identified issues
- Run this workflow again
- Contact support if API issues persist
'''
    save_issue_content(error_issue)


def save_issue_content(content):
    """Save issue content to file for GitHub CLI."""
    with open('preview_issue.md', 'w', encoding='utf-8') as f:
        f.write(content)


if __name__ == '__main__':
    success = test_apis_and_create_issue()
    sys.exit(0 if success else 1)