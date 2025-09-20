# Queue Title Editor

The queue title editor allows you to customize article titles before they are posted to Twitter. This gives you control over how your tweets will appear without modifying the original article content.

## Quick Start

```bash
# Interactive editing
python edit_queue_titles.py

# Show demo of functionality  
python demo_edit_queue.py
```

## Features

- ✏️ **Interactive editing**: Edit titles one by one with real-time preview
- 📦 **Batch mode**: Select multiple articles to edit in sequence
- 📱 **Tweet preview**: See exactly how tweets will look with new titles
- 📊 **Character counting**: Ensure tweets stay within Twitter's 280-character limit
- 💾 **Safe editing**: Changes only saved when you confirm
- 🔄 **Fallback protection**: Original article content remains unchanged

## How It Works

1. **Load Queue**: Reads articles from `posted_articles.json`
2. **Edit Titles**: Modify the `title` field of queued articles
3. **Preview Tweets**: Shows how tweets will look with new titles
4. **Save Changes**: Updates the queue with your edits

## Usage Examples

### Interactive Mode
```bash
python edit_queue_titles.py
# Choose option 1 for interactive editing
# Select article numbers to edit
# Enter new titles and preview tweets
# Save when satisfied
```

### Quick Demo
```bash
python demo_edit_queue.py
# Shows current queue and demonstrates editing
```

## Use Cases

- **Improve engagement**: Make titles more compelling for Twitter
- **Fix formatting**: Remove technical jargon or lengthy descriptions  
- **Customize content**: Tailor titles for your specific audience
- **Character optimization**: Ensure tweets fit within limits
- **Brand consistency**: Adjust tone and style to match your brand

## Safety Features

- **Backup preserved**: Original article content never modified
- **Preview before save**: See tweet changes before committing
- **Validation**: Warns about very short/long titles
- **Cancel anytime**: Exit without saving changes
- **Character limits**: Prevents tweets over 280 characters

## File Structure

```
edit_queue_titles.py    # Main interactive editor
demo_edit_queue.py      # Demonstration script
show_queued_tweets.py   # Preview tweets without editing
show_queue_simple.py    # Simple queue overview
```

The editor integrates seamlessly with the existing bot workflow - edited titles will be used when the bot posts tweets automatically.