# Gemini AI Integration Troubleshooting

## The Problem
The bot was generating malformed tweets with incorrect grammar like:
- "Rail Boss invests $12 M in BTC mining via Stole Electricity" 
- Missing 3-point summaries

## Root Causes Identified

### 1. **Gemini API Not Configured**
The bot falls back to enhanced text processing when `GEMINI_API_KEY` is not set, but the fallback logic had bugs.

### 2. **Poor Entity Extraction**
The entity extraction was incorrectly parsing titles like "Rail Boss 'Stole Electricity..." as two companies: "Rail Boss" and "Stole Electricity".

### 3. **Inappropriate Template Usage**
The company investment template "X invests Y via Z" was being used for crime/scandal stories where it doesn't make sense.

## Fixes Applied

### 1. **Improved Entity Extraction**
- Added negative keyword filtering to avoid extracting crime-related terms as companies
- Fixed regex patterns to properly identify legitimate companies
- Added exclusion list for words like 'stole', 'steal', 'boss', 'arrest', etc.

### 2. **Smarter Template Selection**
- Added detection for negative news (crime, scandal, theft)
- Route negative news to generic format instead of company format
- Only use company format for actual business announcements

### 3. **Enhanced Gemini Prompts**
- Improved prompts for better headline generation
- Better character limits and fallback handling
- More specific requirements for different types of news

## How to Enable Gemini AI

To get proper AI-generated headlines and 3-point summaries:

1. **Get a Gemini API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create an API key

2. **Set Environment Variable**:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

3. **For GitHub Actions**:
   - Add `GEMINI_API_KEY` to repository secrets
   - The bot will automatically use it

## Expected Behavior

**With Gemini API configured:**
- Headlines: AI-generated engaging headlines using URL context analysis
- Summaries: 3-point bulleted summaries based on full article content
- Format: "Headline\n\n• Point 1 • Point 2 • Point 3"
- Enhanced accuracy: Analyzes actual article content from URLs for better insights

**Without Gemini API (fallback):**
- Headlines: Enhanced processing with financial amounts
- Format: "$12 M: Original Article Title" or similar
- No 3-point summaries

## New URL Context Feature

The bot now uses Gemini's **URL Context tool** to provide enhanced analysis:

### What It Does
- Fetches and analyzes the full content of news article URLs
- Provides more accurate headlines based on complete article context
- Generates better summaries using actual article data
- Combines title/summary with deep URL content analysis

### How It Works
```python
# The bot automatically enables URL context for every article
tools = [{"url_context": {}}]

# Gemini analyzes the full article content from the URL
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt_with_url_reference,
    config=GenerateContentConfig(tools=tools)
)
```

### Benefits
- **Higher Accuracy**: Analysis based on complete article content
- **Better Context**: Understanding of nuanced financial/technical details  
- **Improved Headlines**: More engaging and precise tweet content
- **Real-time Content**: Access to the latest article updates

## Validation

Run this to test your setup:
```bash
python bot.py --diagnose
```

Look for:
- ✅ GEMINI_API_KEY: SET (if configured)
- ⚠️ GEMINI_API_KEY: NOT SET (if missing)