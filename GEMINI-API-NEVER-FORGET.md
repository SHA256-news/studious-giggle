# 🚨 CRITICAL: Gemini URL Context Implementation - FOREVER REFERENCE

## ⚠️ THE SYSTEMATIC PROBLEM WE SOLVED:

**User's exact words**: *"every single time that i've had you refactor code, you've forgotten how to use the gemini API - it's systematic!!"*

**Root Cause**: Mixing REST API dict format with Python SDK complex object format

---

## ✅ THE ONE TRUE FORMAT - NEVER CHANGE THIS:

```python
# ✅ ALWAYS USE THIS FORMAT - NEVER CHANGE!
config = {
    "tools": [{"url_context": {}}]
}

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=config
)
```

**Source**: Official Google Cookbook examples:
- Grounding.ipynb lines 561, 696, 873  
- Multiple confirmed working examples
- REST API compatibility
- Simple, error-proof syntax

---

## ❌ FORMATS THAT CAUSE "UNABLE TO FETCH CONTENT" TWEETS:

### ❌ NEVER USE: Complex Type Objects
```python
# ❌ THIS CAUSES ERROR TWEETS!
from google.genai import types
tools = [types.Tool(url_context=types.UrlContext())]  # ← WRONG!
config = types.GenerateContentConfig(tools=tools)
```

### ❌ NEVER USE: Mixed Formats  
```python
# ❌ THIS ALSO CAUSES ERRORS!
config = {
    "tools": [types.Tool(url_context=types.UrlContext())]  # ← WRONG!
}
```

---

## 🔒 IMPLEMENTATION RULES:

### 1. Client Initialization:
```python
from google import genai

# ✅ SIMPLE - No types import needed
client = genai.Client(api_key=api_key)
```

### 2. Tool Configuration:
```python
# ✅ SIMPLE DICT - Always use this exact format
config = {
    "tools": [{"url_context": {}}]
}
```

### 3. API Call:
```python
# ✅ SIMPLE - URL goes in prompt, tool handles the rest
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Analyze this article: {url}",
    config=config
)
```

### 4. Response Handling:
```python
# ✅ SIMPLE - Direct text access
text = response.text

# ✅ OPTIONAL - Check retrieval status
if hasattr(response, 'candidates') and response.candidates:
    candidate = response.candidates[0]
    if hasattr(candidate, 'url_context_metadata'):
        print(candidate.url_context_metadata)
```

---

## 🧬 PERMANENT CLASS PATTERN:

```python
class GeminiClient:
    def __init__(self, api_key: str):
        from google import genai
        # ✅ NO TYPES IMPORT - Use simple dicts only
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash'
    
    def generate_content(self, prompt: str, url: str = None):
        if url:
            prompt = f"{prompt}\n\nURL: {url}"
        
        # ✅ ALWAYS USE SIMPLE DICT FORMAT
        config = {
            "tools": [{"url_context": {}}]
        }
        
        return self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config
        )
```

---

## 🔍 HOW TO DETECT WRONG IMPLEMENTATION:

**Symptoms of Wrong Format:**
- Bot posts tweets like: "I am unable to access the content..."
- Bot posts: "I cannot fetch the content from the URL..."
- Bot posts: "Failed to retrieve content from..."

**Debug Check:**
```python
# If you see this in logs, format is WRONG:
# "Generated headline with URL context: 'I am unable to access the content...'"

# Should see this instead:
# "Generated headline with URL context: 'Marathon Digital Deploys 5,000 New Miners'"
```

---

## 📚 OFFICIAL SOURCES (VERIFIED):

1. **Official Google Docs**: https://ai.google.dev/gemini-api/docs/url-context
2. **Working Cookbook**: https://github.com/google-gemini/cookbook/tree/main/quickstarts/Grounding.ipynb
3. **Verified Lines**: 561, 696, 873 (all use simple dict format)
4. **JavaScript Examples**: Use `{ urlContext: {} }` (equivalent simple format)

---

## 🚨 EMERGENCY RECOVERY PROCEDURE:

**If bot starts posting error messages again:**

1. **IMMEDIATE**: Check tool configuration in core.py
2. **VERIFY**: Look for `{"url_context": {}}` simple dict format
3. **REPLACE**: Any complex `types.Tool(...)` with simple dict
4. **TEST**: Verify response.text contains actual content, not error messages

---

## 💾 PERMANENT COMMIT MESSAGE TEMPLATE:

```
Fix: Use simple dict format for Gemini URL context tools

- Replace complex types.Tool() objects with {"url_context": {}} dict
- Prevents "unable to fetch content" error tweets
- Follows official Google cookbook examples (Grounding.ipynb)
- Ensures URL context properly retrieves article content

CRITICAL: Never use types.Tool(url_context=types.UrlContext()) format!
```

---

**GOLDEN RULE**: When in doubt, use the simple dict format `{"url_context": {}}` - it ALWAYS works!