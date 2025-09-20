#!/usr/bin/env python3
"""
Edit Queue Titles
-----------------
Interactive tool to edit article titles in the queue before they are posted to Twitter.
This allows customizing the content without affecting the original article data.
"""

import json
import logging
import os
import sys
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Import utilities
from utils import TextUtils, FileManager


def load_queue_data() -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Load the complete posted articles data and extract queued articles"""
    posted_articles = FileManager.load_posted_articles()
    queued_articles = posted_articles.get("queued_articles", [])
    return posted_articles, queued_articles


def save_queue_data(posted_articles: Dict[str, Any]) -> None:
    """Save the updated queue data back to file"""
    FileManager.save_posted_articles(posted_articles)


def show_queue_list(queued_articles: List[Dict[str, Any]]) -> None:
    """Display a numbered list of articles in the queue"""
    print("\n📋 CURRENT QUEUE")
    print("=" * 80)
    
    if not queued_articles:
        print("📭 No articles in queue")
        return
    
    for i, article in enumerate(queued_articles, 1):
        title = article.get("title", "Unknown Title")
        source = article.get("source", {}).get("title", "Unknown Source")
        date = article.get("date", "Unknown Date")
        
        # Show current tweet preview
        try:
            tweet_preview = TextUtils.create_enhanced_tweet_text(article)
            tweet_chars = len(tweet_preview)
        except Exception:
            tweet_preview = "Error generating preview"
            tweet_chars = 0
        
        print(f"\n{i:2d}. {title}")
        print(f"    Source: {source} | Date: {date}")
        print(f"    Tweet: {tweet_preview}")
        print(f"    Characters: {tweet_chars}/280")


def show_article_details(article: Dict[str, Any], index: int) -> None:
    """Show detailed information about a specific article"""
    print(f"\n{'='*80}")
    print(f"📰 ARTICLE #{index} DETAILS")
    print(f"{'='*80}")
    
    title = article.get("title", "Unknown Title")
    source = article.get("source", {}).get("title", "Unknown Source")
    date = article.get("date", "Unknown Date")
    url = article.get("url", "No URL")
    
    print(f"📰 Original Article:")
    print(f"   Title: {title}")
    print(f"   Source: {source}")
    print(f"   Date: {date}")
    print(f"   URL: {url[:60]}{'...' if len(url) > 60 else ''}")
    
    # Show current tweet formats
    try:
        enhanced_tweet = TextUtils.create_enhanced_tweet_text(article)
        original_tweet = TextUtils.create_original_tweet_text(article)
        
        print(f"\n🚀 CURRENT TWEET FORMATS:")
        print(f"┌─ Enhanced Format (Default) ────────────────────────────────────┐")
        print(f"│ {enhanced_tweet:<62} │")
        print(f"└─ Characters: {len(enhanced_tweet):<52} ┘")
        
        print(f"\n📜 Original Format (Fallback):")
        print(f"   {original_tweet}")
        print(f"   Characters: {len(original_tweet)}")
        
    except Exception as e:
        logger.error(f"Error generating tweet preview: {e}")
        print(f"\n❌ Error generating tweet preview: {e}")


def edit_article_title(article: Dict[str, Any], index: int) -> Optional[str]:
    """Edit the title of a specific article"""
    show_article_details(article, index)
    
    current_title = article.get("title", "")
    print(f"\n✏️  EDIT TITLE FOR ARTICLE #{index}")
    print("=" * 50)
    print(f"Current title: {current_title}")
    print("\nEnter new title (or press Enter to keep current title):")
    print("Type 'cancel' to cancel editing this article")
    
    while True:
        try:
            new_title = input("\n> ").strip()
            
            if new_title.lower() == 'cancel':
                print("❌ Cancelled editing this article")
                return None
            
            if not new_title:
                print("✅ Keeping current title unchanged")
                return None
            
            # Validate the new title
            if len(new_title) < 10:
                print("⚠️  Title seems too short (less than 10 characters). Are you sure? (y/n)")
                confirm = input("> ").strip().lower()
                if confirm != 'y':
                    continue
            
            if len(new_title) > 200:
                print("⚠️  Title is quite long. This might affect tweet formatting. Continue? (y/n)")
                confirm = input("> ").strip().lower()
                if confirm != 'y':
                    continue
            
            # Show preview with new title
            test_article = article.copy()
            test_article["title"] = new_title
            
            try:
                test_tweet = TextUtils.create_enhanced_tweet_text(test_article)
                print(f"\n📱 PREVIEW WITH NEW TITLE:")
                print(f"   New title: {new_title}")
                print(f"   Tweet: {test_tweet}")
                print(f"   Characters: {len(test_tweet)}/280")
                
                if len(test_tweet) > 280:
                    print("⚠️  Warning: Tweet exceeds 280 characters and will be truncated!")
                
                print(f"\nConfirm this change? (y/n)")
                confirm = input("> ").strip().lower()
                
                if confirm == 'y':
                    return new_title
                else:
                    print("❌ Change cancelled, try again or type 'cancel' to exit")
                    continue
                    
            except Exception as e:
                print(f"❌ Error generating preview with new title: {e}")
                print("Continue anyway? (y/n)")
                confirm = input("> ").strip().lower()
                
                if confirm == 'y':
                    return new_title
                else:
                    continue
                    
        except KeyboardInterrupt:
            print("\n❌ Cancelled editing")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


def interactive_edit_mode(posted_articles: Dict[str, Any], queued_articles: List[Dict[str, Any]]) -> bool:
    """Interactive mode for editing queue titles"""
    changes_made = False
    
    while True:
        try:
            show_queue_list(queued_articles)
            
            if not queued_articles:
                print("\n📭 No articles to edit")
                break
            
            print(f"\n✏️  EDIT QUEUE TITLES")
            print("=" * 50)
            print("Commands:")
            print("  • Enter a number (1-{}) to edit that article's title".format(len(queued_articles)))
            print("  • Type 'save' to save changes and exit")
            print("  • Type 'exit' to exit without saving")
            print("  • Type 'list' to show the queue again")
            
            choice = input("\n> ").strip().lower()
            
            if choice == 'exit':
                if changes_made:
                    print("⚠️  You have unsaved changes. Save before exiting? (y/n)")
                    save_confirm = input("> ").strip().lower()
                    if save_confirm == 'y':
                        save_queue_data(posted_articles)
                        print("✅ Changes saved!")
                        return True
                    else:
                        print("❌ Exiting without saving changes")
                        return False
                else:
                    print("👋 No changes made, exiting")
                    return False
            
            elif choice == 'save':
                if changes_made:
                    save_queue_data(posted_articles)
                    print("✅ All changes saved successfully!")
                    return True
                else:
                    print("📝 No changes to save")
                    return False
            
            elif choice == 'list':
                continue  # This will show the list again
            
            elif choice.isdigit():
                article_num = int(choice)
                if 1 <= article_num <= len(queued_articles):
                    article_index = article_num - 1
                    article = queued_articles[article_index]
                    
                    new_title = edit_article_title(article, article_num)
                    
                    if new_title:
                        # Update the title in the article
                        article["title"] = new_title
                        changes_made = True
                        print(f"✅ Updated title for article #{article_num}")
                    
                else:
                    print(f"❌ Invalid article number. Please enter 1-{len(queued_articles)}")
            
            else:
                print("❌ Invalid command. Try again.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            if changes_made:
                print("⚠️  You have unsaved changes. Save before exiting? (y/n)")
                try:
                    save_confirm = input("> ").strip().lower()
                    if save_confirm == 'y':
                        save_queue_data(posted_articles)
                        print("✅ Changes saved!")
                        return True
                except KeyboardInterrupt:
                    print("\n❌ Exiting without saving")
                    return False
            return False
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}")
            print(f"❌ Error: {e}")
            continue


def batch_edit_mode(posted_articles: Dict[str, Any], queued_articles: List[Dict[str, Any]]) -> bool:
    """Batch edit mode - edit specific articles by number"""
    if not queued_articles:
        print("📭 No articles in queue to edit")
        return False
    
    show_queue_list(queued_articles)
    
    print(f"\n✏️  BATCH EDIT MODE")
    print("=" * 50)
    print("Enter article numbers to edit (comma-separated, e.g., '1,3,5')")
    print("Or type 'all' to edit all articles")
    print("Type 'cancel' to return to main menu")
    
    try:
        choice = input("\n> ").strip().lower()
        
        if choice == 'cancel':
            return False
        
        if choice == 'all':
            article_indices = list(range(len(queued_articles)))
        else:
            # Parse comma-separated numbers
            try:
                numbers = [int(x.strip()) for x in choice.split(',')]
                article_indices = [n - 1 for n in numbers if 1 <= n <= len(queued_articles)]
                
                if not article_indices:
                    print("❌ No valid article numbers provided")
                    return False
                    
            except ValueError:
                print("❌ Invalid input. Please enter numbers separated by commas")
                return False
        
        # Edit each selected article
        changes_made = False
        for i in article_indices:
            article = queued_articles[i]
            article_num = i + 1
            
            new_title = edit_article_title(article, article_num)
            
            if new_title:
                article["title"] = new_title
                changes_made = True
                print(f"✅ Updated title for article #{article_num}")
            
            # Ask if user wants to continue after each edit
            if i < len(article_indices) - 1:  # Not the last article
                print(f"\nContinue to next article? (y/n)")
                continue_edit = input("> ").strip().lower()
                if continue_edit != 'y':
                    break
        
        if changes_made:
            save_queue_data(posted_articles)
            print("✅ All changes saved!")
            return True
        else:
            print("📝 No changes made")
            return False
            
    except KeyboardInterrupt:
        print("\n❌ Batch edit cancelled")
        return False


def main():
    """Main function for the queue title editor"""
    print("✏️  QUEUE TITLE EDITOR")
    print("=" * 80)
    print("Edit article titles in the queue before they are posted to Twitter")
    print("=" * 80)
    
    # Load queue data
    try:
        posted_articles, queued_articles = load_queue_data()
    except Exception as e:
        logger.error(f"Error loading queue data: {e}")
        print(f"❌ Error loading queue data: {e}")
        return 1
    
    if not queued_articles:
        print("📭 No articles currently in the queue!")
        print("\nTo add articles to the queue:")
        print("1. Run the bot normally: python bot.py")
        print("2. The bot will fetch new articles and queue them")
        print("3. Run this script again to edit titles")
        return 0
    
    # Show initial queue status
    print(f"📊 Found {len(queued_articles)} articles in queue")
    
    # Main menu
    while True:
        try:
            print(f"\n🎛️  MAIN MENU")
            print("=" * 40)
            print("1. Interactive Edit Mode (edit one at a time)")
            print("2. Batch Edit Mode (select multiple)")
            print("3. Show Queue List")
            print("4. Exit")
            
            choice = input("\nChoose an option (1-4): ").strip()
            
            if choice == '1':
                success = interactive_edit_mode(posted_articles, queued_articles)
                if success:
                    print("\n✅ Queue editing completed successfully!")
                    break
            
            elif choice == '2':
                success = batch_edit_mode(posted_articles, queued_articles)
                if success:
                    print("\n✅ Batch editing completed successfully!")
                    break
            
            elif choice == '3':
                show_queue_list(queued_articles)
            
            elif choice == '4':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid option. Please choose 1-4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error in main menu: {e}")
            print(f"❌ Error: {e}")
            continue
    
    return 0


if __name__ == "__main__":
    sys.exit(main())