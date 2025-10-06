# Google Gemini API Reference

> **CRITICAL**: This is the permanent API reference for Google Gemini. Always reference this during refactoring!

## ⚠️ Critical Error Handling (October 2025 Update)

**URLRetrievalError Exception Pattern**:
When using URL context, always check metadata safely to prevent crashes:

```python
# ✅ CORRECT: Safe metadata checking
if hasattr(response, 'candidates') and response.candidates:
    candidate = response.candidates[0]
    if hasattr(candidate, 'url_context_metadata'):
        metadata = candidate.url_context_metadata
        if metadata is not None:
            try:
                # Handle both single item and iterable metadata
                metadata_items = metadata if hasattr(metadata, '__iter__') and not isinstance(metadata, (str, bytes)) else [metadata]
                
                for url_metadata in metadata_items:
                    if hasattr(url_metadata, 'url_retrieval_status'):
                        status = str(url_metadata.url_retrieval_status)
                        if 'ERROR' in status or 'FAILED' in status:
                            raise URLRetrievalError(f"URL retrieval failed: {status}")
            except TypeError:
                # Continue without raising exception for metadata parsing issues
                pass
```

## Installation & Setup

```python
pip install google-genai

from google import genai
from google.genai import types

# Initialize client
client = genai.Client(api_key="YOUR_API_KEY")
```

## Core Models

### Gemini 2.5 Flash
- **Model ID**: `"gemini-2.5-flash"`
- **Context Window**: 1 million tokens
- **Best For**: Balanced performance, URL context, threading
- **Used In Bot**: Primary model for content generation

### Gemini 2.5 Pro  
- **Model ID**: `"gemini-2.5-pro"`
- **Context Window**: 2 million tokens
- **Best For**: Complex reasoning tasks
- **Rate Limits**: More restrictive than Flash

## Content Generation

### Basic Text Generation

```python
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write a catchy headline about Bitcoin mining"
)

print(response.text)
```

### Advanced Configuration

```python
from google.genai import types

# Configure generation parameters
config = types.GenerateContentConfig(
    temperature=0.7,        # Creativity (0.0-1.0)
    top_p=0.8,             # Nucleus sampling
    max_output_tokens=150,  # Response length limit
    candidate_count=1,      # Number of responses
    stop_sequences=["\n\n"] # Stop generation at sequences
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Generate content here",
    config=config
)
```

## URL Context Tool (CRITICAL FOR BOT)

**MOST IMPORTANT FEATURE**: Gemini can fetch and analyze web page content directly.

```python
from google.genai import types

# Enable URL context tool
config = types.GenerateContentConfig(
    tools=[types.Tool(url_context=types.UrlContext())]
)

prompt = f"""
Analyze the article at {article_url} and create a catchy headline.

Requirements:
- 60-80 characters
- Include specific facts from the article
- No emojis or hashtags
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=config
)

headline = response.text.strip()
```

### URL Context Metadata (CRITICAL - Error Detection)

```python
# Access URL context metadata and detect failures
if hasattr(response, 'candidates') and response.candidates:
    candidate = response.candidates[0]
    if hasattr(candidate, 'url_context_metadata'):
        metadata = candidate.url_context_metadata
        
        # CRITICAL: Check for URL retrieval failures
        for url_metadata in metadata:
            if hasattr(url_metadata, 'url_retrieval_status'):
                status = str(url_metadata.url_retrieval_status)
                if 'ERROR' in status or 'FAILED' in status:
                    # URL retrieval failed - raise exception to skip article
                    raise URLRetrievalError(f"Failed to retrieve content from URL: {status}")
        
        print(f"Fetched URL: {url_metadata.retrieved_url}")
        print(f"Status: {url_metadata.url_retrieval_status}")
```

## Bot-Specific Patterns

### 1. Headline Generation with URL Context (Error-Safe)

```python
class URLRetrievalError(Exception):
    """Raised when URL content retrieval fails."""
    pass

def generate_catchy_headline(article_url: str, title: str) -> str:
    """Generate AI-powered headline using full article content."""
    
    config = types.GenerateContentConfig(
        tools=[types.Tool(url_context=types.UrlContext())],
        temperature=0.7,
        max_output_tokens=100
    )
    
    prompt = f"""
    Create a compelling Bitcoin mining headline for: {article_url}
    
    Requirements:
    - 60-80 characters maximum
    - Include specific numbers/facts from article
    - Use action words (surges, drops, announces, reaches)
    - NO emojis, hashtags, or special characters
    - Professional news style
    
    Return only the headline text.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
        
        # CRITICAL: Check URL retrieval status before using response
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'url_context_metadata'):
                for url_metadata in candidate.url_context_metadata:
                    if hasattr(url_metadata, 'url_retrieval_status'):
                        status = str(url_metadata.url_retrieval_status)
                        if 'ERROR' in status or 'FAILED' in status:
                            raise URLRetrievalError(f"Failed to retrieve content from {article_url}: {status}")
        
        return response.text.strip()[:80]
        
    except URLRetrievalError:
        # Let URL retrieval errors bubble up - bot will skip this article
        raise
    except ValueError as e:
        # API authentication issues
        print(f"Gemini auth error: {e}")
        raise
    except Exception as e:
        print(f"Gemini error: {e}")
        return title[:80]  # Fallback to original title
```

### 2. Summary Generation (Anti-Repetition)

```python
def generate_thread_summary(article_url: str, headline: str) -> str:
    """Generate summary that complements headline without repetition."""
    
    config = types.GenerateContentConfig(
        tools=[types.Tool(url_context=types.UrlContext())],
        temperature=0.6,
        max_output_tokens=200
    )
    
    prompt = f"""
    Read the article at {article_url} and create a 3-point summary.
    
    Generated Headline: {headline}
    
    CRITICAL: DO NOT repeat any information from the headline above.
    
    Requirements:
    - Total under 180 characters
    - Format: Each point starts with "•"
    - Focus on NEW details not in headline
    - Include specifics: numbers, dates, locations
    - No periods at end of bullet points
    
    Return only the formatted summary.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
        return process_summary_response(response.text.strip())
        
    except Exception as e:
        print(f"Gemini summary error: {e}")
        return "• Bitcoin mining sector update\n• Industry development\n• See article for details"
```

### 3. Combined Content Generation

```python
def create_twitter_thread_content(article_url: str) -> tuple[str, str]:
    """Generate both headline and summary for Twitter thread."""
    
    # Step 1: Generate headline first
    headline = generate_catchy_headline(article_url, "")
    
    # Step 2: Generate summary that avoids headline repetition
    summary = generate_thread_summary(article_url, headline)
    
    return headline, summary
```

## Error Handling

### Common Error Types

```python
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config
    )
    
except ValueError as e:
    # API key issues, authentication problems
    print(f"Authentication error: {e}")
    raise  # Re-raise for bot to handle
    
except ConnectionError as e:
    # Network connectivity issues
    print(f"Network error: {e}")
    return fallback_content
    
except Exception as e:
    # Other unexpected errors
    print(f"Unexpected Gemini error: {e}")
    return fallback_content
```

### Rate Limiting

```python
import time
from google.api_core import exceptions

def generate_with_retry(prompt: str, max_retries: int = 3) -> str:
    """Generate content with automatic retry on rate limits."""
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text.strip()
            
        except exceptions.ResourceExhausted:
            # Rate limit hit
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"Generation failed on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
    
    raise Exception("Max retries exceeded")
```

## Response Processing

### Text Cleaning

```python
import re

def clean_response_text(text: str) -> str:
    """Clean and normalize Gemini response text."""
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    
    # Remove emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs  
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
```

### Summary Processing

```python
def process_summary_response(summary_text: str) -> str:
    """Process summary response into proper bullet format."""
    
    # Remove numbering (1. 2. 3.)
    summary_text = re.sub(r'^\d+\.\s*', '', summary_text, flags=re.MULTILINE)
    
    # Convert inline bullets to line breaks
    if ' • ' in summary_text and '\n' not in summary_text:
        parts = [part.strip() for part in summary_text.split(' • ') if part.strip()]
        summary_text = '\n'.join([f'• {part}' if not part.startswith('•') else part for part in parts[:3]])
    
    # Ensure proper bullet formatting
    elif '\n' in summary_text:
        lines = [line.strip() for line in summary_text.split('\n') if line.strip()]
        summary_text = '\n'.join([f'• {line}' if not line.startswith('•') else line for line in lines[:3]])
    
    else:
        summary_text = f'• {summary_text}'
    
    # Remove trailing periods (keep question marks)
    lines = summary_text.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip():
            if line.rstrip().endswith('.') and not line.rstrip().endswith('?'):
                line = line.rstrip()[:-1]
            cleaned_lines.append(line)
    
    summary_text = '\n'.join(cleaned_lines)
    
    # Ensure length limit (180 chars)
    if len(summary_text) > 180:
        lines = summary_text.split('\n')
        result_lines = []
        total_length = 0
        
        for line in lines:
            if total_length + len(line) + 1 <= 177:
                result_lines.append(line)
                total_length += len(line) + 1
            else:
                break
        
        summary_text = '\n'.join(result_lines)
        if len(summary_text) > 180:
            summary_text = summary_text[:177] + "..."
    
    return summary_text
```

## API Configuration

### Environment Variables

```python
import os

# Recommended approach
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable required")

client = genai.Client(api_key=api_key)
```

### Client Configuration

```python
# Initialize with custom settings
client = genai.Client(
    api_key="YOUR_API_KEY",
    default_model="gemini-2.5-flash"
)
```

## Bot Integration Checklist

1. **✅ URL Context Enabled**: Always use `tools=[Tool(url_context=UrlContext())]`
2. **✅ Error Handling**: Catch ValueError (auth), ConnectionError (network), Exception (other)
3. **✅ Rate Limiting**: Implement exponential backoff for retries
4. **✅ Response Cleaning**: Remove emojis, markdown, clean whitespace
5. **✅ Length Limits**: Enforce character limits for Twitter (280 chars)
6. **✅ Fallback Content**: Always have fallback when Gemini fails
7. **✅ Anti-Repetition**: Pass headline to summary generation to avoid duplication
8. **✅ Specific Prompts**: Use detailed, specific prompts with examples

## Testing

```python
def test_gemini_connection():
    """Test Gemini API connection and basic functionality."""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Generate a single word: 'SUCCESS'"
        )
        
        if "SUCCESS" in response.text:
            print("✅ Gemini API connection successful")
            return True
        else:
            print("❌ Unexpected response from Gemini")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

# Run test
test_gemini_connection()
```

---

**Last Updated**: 2025-01-05  
**Package Version**: google-genai>=0.1.0  
**Documentation Source**: https://ai.google.dev/gemini-api/docs