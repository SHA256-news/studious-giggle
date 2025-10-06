# Gemini URL Context API - CORRECT Implementation (OCTOBER 2025 MAJOR FIX)

## 🚨 CRITICAL: The Problem We Fixed

The bot was posting error messages as tweets: 
> "I was unable to fetch the content of the article from the provided URL. Therefor..."

**Root Cause Discovered**: Wrong SDK format mixing REST API patterns with Python SDK syntax.

---

## 🔥 OCTOBER 2025 FIX: Python SDK vs REST API Format Confusion

### THE CRITICAL DIFFERENCE WE DISCOVERED

**❌ WRONG - What We Had (REST API Format in Python SDK):**
```python
from google.genai.types import GenerateContentConfig

# ❌ WRONG: We were mixing REST API dict format with Python SDK
config = GenerateContentConfig(
    tools=[{"url_context": {}}]  # This is REST API syntax!
)
```

**✅ CORRECT - Python SDK Format (From Official Cookbook):**
```python
from google.genai import types

# ✅ CORRECT: Python SDK requires proper Tool objects  
tools = []
tools.append(types.Tool(url_context=types.UrlContext()))

config = types.GenerateContentConfig(
    tools=tools
)
```

### 2. Correct Client Initialization
```python
client = genai.Client(api_key=api_key)
model_id = "gemini-2.5-flash"
```

### 3. Correct Tool Configuration (CRITICAL)
```python
# ✅ CORRECT: Simple dict format from official docs
tools = [{"url_context": {}}]

config = GenerateContentConfig(tools=tools)

# ❌ WRONG: Complex object format (what we had before)
# tools = [types.Tool(url_context=types.UrlContext())]
```

### 4. Correct API Call Pattern
```python
response = client.models.generate_content(
    model=model_id,
    contents=f"Analyze this article: {url}",
    config=GenerateContentConfig(
        tools=[{"url_context": {}}]
    )
)
```

### 5. Correct Response Handling & Status Checking (October 2025 FIX)

```python
# ✅ CORRECT: Comprehensive response processing with proper status checking
if hasattr(response, 'candidates') and response.candidates:
    candidate = response.candidates[0]
    if hasattr(candidate, 'url_context_metadata') and candidate.url_context_metadata:
        metadata = candidate.url_context_metadata
        
        # CRITICAL: Proper status checking for enum values
        if hasattr(metadata, 'url_metadata'):
            for url_meta in metadata.url_metadata:
                if hasattr(url_meta, 'url_retrieval_status'):
                    status = url_meta.url_retrieval_status
                    status_str = str(status)
                    
                    # ✅ CORRECT: Handle both enum value and string representation
                    is_success = (
                        status_str == "URL_RETRIEVAL_STATUS_SUCCESS" or 
                        "URL_RETRIEVAL_STATUS_SUCCESS" in status_str
                    )
                    
                    if not is_success:
                        # URL retrieval failed
                        raise URLRetrievalError(f"Failed to retrieve content from {url}: {status_str}")
                    else:
                        # URL retrieval succeeded - continue processing
                        logger.info(f"✅ URL retrieval successful: {status_str}")

# Get the actual content
text = response.text.strip()

# ❌ WRONG Status Checking (What Caused The Bug):
# if str(status) != "URL_RETRIEVAL_STATUS_SUCCESS":
#     # This fails because enum includes class name: "UrlRetrievalStatus.URL_RETRIEVAL_STATUS_SUCCESS"
```
```python
# Access the generated text
text_content = response.text

# Check URL retrieval status (official pattern)
if response.candidates[0].url_context_metadata:
    for url_meta in response.candidates[0].url_context_metadata.url_metadata:
        status = url_meta.url_retrieval_status
        retrieved_url = url_meta.retrieved_url
        print(f"URL: {retrieved_url}, Status: {status}")
```

---

## 📋 Complete Working Example (From Official Docs)

```python
from google import genai
from google.genai.types import GenerateContentConfig

client = genai.Client(api_key="your-api-key")
model_id = "gemini-2.5-flash"

url1 = "https://www.example.com/article"
url2 = "https://www.example.com/article2"

response = client.models.generate_content(
    model=model_id,
    contents=f"Compare the content from {url1} and {url2}",
    config=GenerateContentConfig(
        tools=[{"url_context": {}}]
    )
)

# Get the generated content
for part in response.candidates[0].content.parts:
    print(part.text)

# Check URL retrieval status
print(response.candidates[0].url_context_metadata)
```

---

## 🔧 What We Had Wrong Before

### ❌ Wrong Import Pattern
```python
# This was mixing old google-generativeai with new google-genai
from google.genai import types
tools = [types.Tool(url_context=types.UrlContext())]
```

### ❌ Wrong Tool Configuration  
```python
# Complex object-based configuration (outdated pattern)
tools = [self.types.Tool(url_context=self.types.UrlContext())]
```

### ❌ Wrong Response Access
```python
# Overly complex metadata parsing
if hasattr(response, 'candidates'):
    # Complex nested checks...
```

---

## ✅ The Fix Applied

### Before (BROKEN):
```python
def __init__(self, api_key: str):
    from google import genai  
    from google.genai import types  # ❌ WRONG
    self.client = genai.Client(api_key=api_key)
    self.types = types  # ❌ WRONG

def generate_headline(self, article):
    config = self.types.GenerateContentConfig(
        tools=[self.types.Tool(url_context=self.types.UrlContext())]  # ❌ WRONG
    )
```

### After (CORRECT):
```python
def __init__(self, api_key: str):
    from google import genai
    from google.genai.types import GenerateContentConfig  # ✅ CORRECT
    self.client = genai.Client(api_key=api_key)
    self.GenerateContentConfig = GenerateContentConfig  # ✅ CORRECT

def generate_headline(self, article):
    config = self.GenerateContentConfig(
        tools=[{"url_context": {}}]  # ✅ CORRECT: Simple dict format
    )
```

---

## 📚 References

- **Official URL Context Documentation**: https://ai.google.dev/gemini-api/docs/url-context
- **Official Cookbook Examples**: https://github.com/google-gemini/cookbook/tree/main/quickstarts/Grounding.ipynb
- **Working Example Line 642-671**: Shows exact pattern with `tools=[{"url_context": {}}]`

---

## 🎯 Expected Behavior After Fix

✅ **Before**: Bot posts error messages as tweets  
✅ **After**: Bot fetches actual article content and generates proper headlines/summaries

✅ **Before**: "I was unable to fetch the content..."  
✅ **After**: "Marathon Digital Deploys 5,000 New Miners in Texas Facility"

---

## 🧪 Validation Tests

1. **API Configuration Test**: Ensure tool configuration uses simple dict format
2. **URL Retrieval Test**: Verify `url_context_metadata` shows `URL_RETRIEVAL_STATUS_SUCCESS`  
3. **Content Generation Test**: Confirm response contains actual article content, not error messages
4. **Error Detection Test**: Validate that URL failures are properly categorized vs API failures

This documentation serves as the permanent reference for correct Gemini URL Context API usage.

```python
# CORRECT - From official Google documentation
from google import genai
from google.genai.types import GenerateContentConfig

client = genai.Client(api_key=GOOGLE_API_KEY)

config = GenerateContentConfig(
    tools=[{"url_context": {}}]  # Simple dict format, NOT complex objects
)

# URL must be IN the prompt, tool fetches it automatically
prompt = f"Create a headline based on this article: {article.url}"

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=config
)
```

## 🔍 Root Cause Analysis

1. **Wrong SDK Usage**: We're mixing old `google-generativeai` patterns with new `google-genai` SDK
2. **Wrong Tool Definition**: Tools should be simple dicts `{"url_context": {}}`, not complex objects
3. **Correct URL Handling**: URLs go in prompt text, API fetches automatically
4. **Proper Metadata Access**: `response.candidates[0].url_context_metadata` is straightforward

## 📋 Official API Specification

### Tool Configuration:
```python
tools = [{"url_context": {}}]  # Simple dictionary format
```

### Response Metadata Format:
```python
{
  "candidates": [
    {
      "url_context_metadata": {
        "url_metadata": [
          {
            "retrieved_url": "https://example.com/article",
            "url_retrieval_status": "URL_RETRIEVAL_STATUS_SUCCESS"
          }
        ]
      }
    }
  ]
}
```

### URL Retrieval Status Values:
- `URL_RETRIEVAL_STATUS_SUCCESS` - URL accessed successfully
- `URL_RETRIEVAL_STATUS_UNSAFE` - URL failed safety check  
- `URL_RETRIEVAL_STATUS_ERROR` - General retrieval error

## 🚀 Working Examples from Official Cookbook

### Basic URL Context:
```python
from google import genai
from google.genai.types import GenerateContentConfig

client = genai.Client(api_key=GOOGLE_API_KEY)

prompt = """
Based on https://ai.google.dev/gemini-api/docs/models, what are the key 
differences between Gemini models?
"""

config = GenerateContentConfig(
    tools=[{"url_context": {}}]
)

response = client.models.generate_content(
    contents=[prompt],
    model="gemini-2.5-flash",
    config=config
)

print(response.text)
print(response.candidates[0].url_context_metadata)
```

### Multiple URLs:
```python
prompt = f"""
Compare the content from {url1} and {url2}
"""

config = GenerateContentConfig(
    tools=[{"url_context": {}}]
)

response = client.models.generate_content(
    model="gemini-2.5-flash", 
    contents=prompt,
    config=config
)
```

### Combined with Search:
```python
config = GenerateContentConfig(
    tools=[
        {"url_context": {}},
        {"google_search": {}}
    ]
)
```

## 🔧 Implementation Requirements

1. **Use google-genai SDK v1.16.0+**
2. **Simple dict-based tool configuration**
3. **URLs included in prompt text**
4. **Direct metadata access pattern**
5. **Proper error status checking**

## 📊 API Limitations & Features

- **Max URLs per request**: 20
- **Max content per URL**: 34MB
- **Supported models**: gemini-2.5-flash, gemini-2.5-pro, gemini-2.5-flash-lite
- **Supported content**: HTML, PDF, images, JSON, text files
- **Two-step retrieval**: Internal cache → live fetch fallback

## 🛠️ Correct Error Handling Pattern (October 2025 Fixed)

```python
# ✅ CORRECT: Proper URL retrieval status checking
metadata = response.candidates[0].url_context_metadata
for url_meta in metadata.url_metadata:
    status = url_meta.url_retrieval_status
    status_str = str(status)
    
    # Handle both enum value and string representation
    is_success = (
        status_str == "URL_RETRIEVAL_STATUS_SUCCESS" or 
        "URL_RETRIEVAL_STATUS_SUCCESS" in status_str
    )
    
    if not is_success:
        # Handle specific failure - URL was inaccessible
        raise URLRetrievalError(f"Failed to retrieve content: {status_str}")
    else:
        logger.info(f"✅ URL retrieval successful: {status_str}")

# ❌ WRONG Pattern (Caused October 2025 Bug):
# if url_meta.url_retrieval_status != "URL_RETRIEVAL_STATUS_SUCCESS":
#     # This fails because enum value is "UrlRetrievalStatus.URL_RETRIEVAL_STATUS_SUCCESS"
```

## 🐛 Common Bug: Status Checking Logic Error

**Problem**: The enum value includes the class name:
- **Actual enum value**: `UrlRetrievalStatus.URL_RETRIEVAL_STATUS_SUCCESS`
- **Wrong comparison**: `"URL_RETRIEVAL_STATUS_SUCCESS"`
- **Result**: Success treated as failure → Rate limit cooldowns on working URLs!

**Solution**: Use proper string checking that handles both formats.

---
        # This is NOT an API error, it's a content access issue
        logger.warning(f"URL {url_meta.retrieved_url} failed: {url_meta.url_retrieval_status}")
```

## ⚡ Why This Fixes The "Unable to fetch content" Error

The error occurs because:
1. ❌ Our tool configuration is malformed → API can't activate URL context properly
2. ❌ Our prompt format confuses the API → Gemini tries to explain instead of fetch
3. ❌ We're using wrong SDK patterns → Tool initialization fails silently

**With correct implementation**:
1. ✅ Tool activates properly with simple dict format
2. ✅ API automatically fetches URL content  
3. ✅ Gemini receives actual article content, not error messages

## 🎯 Bitcoin Mining Bot Fix Priority

**IMMEDIATE ACTIONS NEEDED**:
1. Update tool configuration to simple dict format
2. Remove complex Type objects for tools
3. Simplify metadata access pattern  
4. Test with known working URLs first
5. Verify response.text contains actual content, not error messages