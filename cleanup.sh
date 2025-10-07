#!/bin/bash
# Cleanup script for old v1.0 files
# Run this to delete old architecture files

echo "🧹 Cleaning up old v1.0 files..."
echo ""

# Delete old code files
echo "Deleting old code files..."
rm -f bot.py
rm -f core.py
rm -f tools.py

# Delete old documentation
echo "Deleting old documentation..."
rm -f BUG-FIXES-OCTOBER-2025.md
rm -f GEMINI-API-NEVER-FORGET.md
rm -f GEMINI_URL_CONTEXT_FIX_OCTOBER_2025.md
rm -f PROMPT-IMPROVEMENTS-NEVER-FORGET.md
rm -f .github/copilot-instructions.md

# Delete old test files
echo "Deleting old test files..."
rm -f show_improved_prompts.py
rm -f test_gemini_fix.py
rm -f test_gemini_headlines.py

# Rename README
echo "Renaming README files..."
if [ -f README.md ]; then
    mv README.md README-OLD.md
fi
if [ -f README-NEW.md ]; then
    mv README-NEW.md README.md
fi

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Old files deleted:"
echo "  - bot.py, core.py, tools.py"
echo "  - Old documentation files"
echo "  - Old test files"
echo ""
echo "README.md updated to new version"
echo ""
echo "Now run:"
echo "  git add -A"
echo "  git commit -m 'v2.0: Clean architecture rebuild'"
echo "  git push"
