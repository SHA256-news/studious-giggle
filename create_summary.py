#!/usr/bin/env python3
"""
Create Twitter thread summaries from generated articles.

This script takes a generated article as input and creates a concise,
multi-tweet thread summary suitable for posting on Twitter.
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime


def clean_text_for_twitter(text):
    """
    Clean text by removing AI processing artifacts and internal thoughts.
    
    Args:
        text (str): Raw text that may contain AI artifacts.
    
    Returns:
        str: Cleaned text suitable for Twitter.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove common AI processing artifacts - more comprehensive patterns
    ai_artifacts = [
        # Browsing/analyzing patterns
        r"I have browsed.*?(?:Now I need to|Let me|I will).*?\.{2,3}",
        r"I am unable to access.*?(?:However|But|Nevertheless).*?\.{2,3}",
        r"Looking at (?:the data|the news|the article).*?\.{2,3}",
        r"Based on (?:the|available|current).*?I can see that.*?\.{2,3}",
        
        # Introductory AI phrases - complete removal
        r"^(?:I need to|Let me|I will|I'm going to|First, I|Now I|Looking at|Based on).*?\.{2,3}\s*",
        r"^(?:Let me (?:analyze|explain|provide|add|mention).*?\.{2,3}\s*)",
        r"^(?:I will now (?:analyze|explain|provide|add|mention).*?\.{2,3}\s*)",
        r"^(?:First, I (?:need to|should|will).*?\.{2,3}\s*)",
        r"^(?:Now I (?:need to|will|can).*?\.{2,3}\s*)",
        
        # Mid-sentence AI artifacts - remove the phrase but keep the content
        r"(?:Let me (?:analyze|explain|provide|add that))\s+",
        r"(?:I will now (?:analyze|explain|provide|add|note|mention))\s+",
        r"(?:First, I (?:need to|should) mention)\s+",
        r"(?:Now I (?:will|need to) (?:analyze|explain|provide))\s+",
        
        # Analysis phrases
        r"I will (?:analyze|provide|explain|add).*?\.{2,3}\s*",
        r"Let me (?:analyze|provide|explain|add).*?\.{2,3}\s*",
        
        # Common AI filler phrases
        r"\.\.\.\s*(?:I will|Let me|Now I|First).*?\.{2,3}",
        r"(?:However|Nevertheless),? I (?:will|can|need to).*?\.{2,3}\s*",
    ]
    
    cleaned = text
    for pattern in ai_artifacts:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean up sentence fragments that start with incomplete words after AI removal
    cleaned = re.sub(r'^(?:should|will|need to|can|might)\s+(?=\w)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^(?:the|that|which|this)\s+(?=\w)', '', cleaned, flags=re.IGNORECASE)
    
    # Capitalize first letter if it becomes lowercase after cleaning
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
    
    # Remove multiple spaces and clean up
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Remove trailing ellipsis if present
    cleaned = re.sub(r'\.{2,}$', '', cleaned).strip()
    
    # Remove leading ellipsis or incomplete sentences
    cleaned = re.sub(r'^\.{2,}\s*', '', cleaned).strip()
    
    # If cleaning removed too much and left a fragment, return empty
    if len(cleaned) < 10 and any(word in cleaned.lower() for word in ['the', 'a', 'an', 'and', 'but', 'or']):
        return ""
    
    return cleaned


def split_text_for_twitter(text, max_length=280, thread_position=None):
    """
    Split text into Twitter-compatible chunks.
    
    Args:
        text (str): Text to split.
        max_length (int): Maximum characters per tweet (default: 280).
        thread_position (tuple): Optional (current, total) for numbering.
    
    Returns:
        list: List of text chunks suitable for Twitter.
    """
    # Clean the text first
    text = clean_text_for_twitter(text)
    
    # Calculate space for thread numbering if provided
    reserved_space = 0
    if thread_position:
        current, total = thread_position
        thread_prefix = f"{current}/{total} "
        reserved_space = len(thread_prefix) + 5  # Extra buffer
    else:
        reserved_space = 10  # Reserve space for potential numbering
    
    effective_length = max_length - reserved_space
    
    # If text fits in one chunk, return it
    if len(text) <= effective_length:
        return [text]
    
    chunks = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Check if adding this sentence would exceed the limit
        test_chunk = f"{current_chunk} {sentence}".strip() if current_chunk else sentence
        
        if len(test_chunk) <= effective_length:
            current_chunk = test_chunk
        else:
            # Save current chunk if it has content
            if current_chunk:
                chunks.append(current_chunk)
            
            # Handle long sentences
            if len(sentence) > effective_length:
                # Split by words
                words = sentence.split()
                temp_chunk = ""
                
                for word in words:
                    test_word_chunk = f"{temp_chunk} {word}".strip() if temp_chunk else word
                    
                    if len(test_word_chunk) <= effective_length:
                        temp_chunk = test_word_chunk
                    else:
                        if temp_chunk:
                            chunks.append(temp_chunk)
                        temp_chunk = word
                
                current_chunk = temp_chunk
            else:
                current_chunk = sentence
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def extract_clean_content(article_data):
    """
    Extract and clean content from article data.
    
    Args:
        article_data (dict): Raw article data.
    
    Returns:
        dict: Cleaned article data.
    """
    # Clean all text fields
    cleaned_data = article_data.copy()
    
    # Clean headline
    if 'headline' in cleaned_data:
        cleaned_data['headline'] = clean_text_for_twitter(cleaned_data['headline'])
    
    # Clean subtitle
    if 'subtitle' in cleaned_data:
        cleaned_data['subtitle'] = clean_text_for_twitter(cleaned_data['subtitle'])
    
    # Clean content
    if 'content' in cleaned_data:
        cleaned_data['content'] = clean_text_for_twitter(cleaned_data['content'])
    
    # Clean key points
    if 'key_points' in cleaned_data and isinstance(cleaned_data['key_points'], list):
        cleaned_data['key_points'] = [
            clean_text_for_twitter(point) for point in cleaned_data['key_points']
        ]
    
    # Clean body
    if 'body' in cleaned_data:
        cleaned_data['body'] = clean_text_for_twitter(cleaned_data['body'])
    
    return cleaned_data


def create_twitter_thread(article_data, max_tweets=10):
    """
    Create a Twitter thread from article data.
    
    Args:
        article_data (dict): Article data with headline, content, and key_points.
        max_tweets (int): Maximum number of tweets in the thread.
    
    Returns:
        list: List of tweets for the thread.
    """
    # Clean the article data first
    article_data = extract_clean_content(article_data)
    
    tweets = []
    
    # Tweet 1: Headline with emoji and hook
    headline = article_data.get('headline', 'Bitcoin Mining Update')
    subtitle = article_data.get('subtitle', '')
    
    # Create engaging first tweet
    first_tweet = f"🧵 {headline}"
    
    # Add subtitle if it fits
    if subtitle and len(first_tweet) + len(subtitle) + 3 < 270:
        first_tweet += f"\n\n{subtitle}"
    
    tweets.append(first_tweet)
    
    # Tweet 2-3: Key points (if available)
    key_points = article_data.get('key_points', [])
    if key_points:
        # Filter out empty or AI artifact points
        clean_points = []
        for point in key_points[:5]:  # Limit to 5 points
            cleaned = clean_text_for_twitter(point)
            if cleaned and len(cleaned) > 10:  # Skip very short/empty points
                clean_points.append(cleaned)
        
        if clean_points:
            key_points_text = "Key takeaways:\n\n"
            for point in clean_points[:3]:  # Max 3 points for brevity
                bullet_point = f"• {point}"
                # Check if adding this point would make it too long
                test_text = key_points_text + bullet_point + "\n"
                if len(test_text) < 270:
                    key_points_text = test_text
            
            key_points_text = key_points_text.strip()
            if len(key_points_text) > 20:  # Only add if meaningful content
                # Split if needed
                chunks = split_text_for_twitter(key_points_text)
                tweets.extend(chunks[:2])  # Max 2 tweets for key points
    
    # Tweet 4-N: Selected content excerpts
    content = article_data.get('content', '') or article_data.get('body', '')
    
    if content:
        # Clean and split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Find the most informative paragraphs
        informative_paragraphs = []
        bitcoin_keywords = ['bitcoin', 'btc', 'mining', 'miner', 'hashrate', 'hash rate', 
                          'difficulty', 'blockchain', 'cryptocurrency', 'asic', 'energy']
        
        for para in paragraphs:
            cleaned_para = clean_text_for_twitter(para)
            # Skip very short paragraphs or ones with AI artifacts
            if len(cleaned_para) < 50:
                continue
            
            # Check for Bitcoin/mining relevance
            para_lower = cleaned_para.lower()
            keyword_count = sum(1 for kw in bitcoin_keywords if kw in para_lower)
            
            if keyword_count >= 2:  # At least 2 relevant keywords
                informative_paragraphs.append(cleaned_para)
        
        # Add the most informative paragraphs as tweets
        remaining_tweets = max_tweets - len(tweets) - 1  # Reserve 1 for conclusion
        
        for para in informative_paragraphs[:3]:  # Max 3 content paragraphs
            if len(tweets) >= max_tweets - 1:
                break
            
            para_chunks = split_text_for_twitter(para)
            # Add only the first chunk of each paragraph to keep thread concise
            if para_chunks:
                tweets.append(para_chunks[0])
    
    # Final tweet: Call to action with relevant hashtags
    tags = article_data.get('tags', ['bitcoin', 'mining', 'cryptocurrency'])
    # Filter and limit tags
    valid_tags = []
    for tag in tags[:3]:
        cleaned_tag = re.sub(r'[^a-zA-Z0-9]', '', tag)
        if cleaned_tag and len(cleaned_tag) > 2:
            valid_tags.append(cleaned_tag)
    
    hashtags = ' '.join([f'#{tag}' for tag in valid_tags[:3]])
    
    final_tweet = "What are your thoughts on these Bitcoin mining developments?"
    if hashtags:
        final_tweet += f"\n\n{hashtags}"
    
    tweets.append(final_tweet)
    
    # Number the tweets
    numbered_tweets = []
    total = len(tweets)
    
    for i, tweet in enumerate(tweets, 1):
        if total > 1:
            numbered_tweet = f"{i}/{total} {tweet}"
            # Ensure it fits in 280 characters
            if len(numbered_tweet) > 280:
                # Truncate and add ellipsis
                max_text_length = 280 - len(f"{i}/{total} ") - 3
                truncated_text = tweet[:max_text_length] + "..."
                numbered_tweet = f"{i}/{total} {truncated_text}"
        else:
            numbered_tweet = tweet
        
        numbered_tweets.append(numbered_tweet)
    
    return numbered_tweets


def main():
    """Main function to create Twitter thread summary from article."""
    parser = argparse.ArgumentParser(description='Create Twitter thread summary from article')
    parser.add_argument('article_file', help='JSON file containing the generated article')
    parser.add_argument('--max-tweets', type=int, default=8,
                       help='Maximum number of tweets in thread (default: 8)')
    parser.add_argument('--output', help='Output file path (default: stdout)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                       help='Output format (default: json)')
    
    args = parser.parse_args()
    
    try:
        # Load article data
        if args.article_file == '-':
            article_data = json.load(sys.stdin)
        else:
            with open(args.article_file, 'r', encoding='utf-8') as f:
                article_data = json.load(f)
        
        # Create Twitter thread
        tweets = create_twitter_thread(article_data, args.max_tweets)
        
        if not tweets:
            print("Failed to create Twitter thread.", file=sys.stderr)
            sys.exit(1)
        
        # Validate tweet lengths
        for i, tweet in enumerate(tweets):
            if len(tweet) > 280:
                print(f"Warning: Tweet {i+1} exceeds 280 characters ({len(tweet)})", file=sys.stderr)
        
        # Prepare output
        if args.format == 'json':
            output_data = {
                'thread': tweets,
                'total_tweets': len(tweets),
                'created_at': datetime.now().isoformat(),
                'source_article': {
                    'headline': article_data.get('headline', ''),
                    'generated_at': article_data.get('generated_at', ''),
                    'source_event_uri': article_data.get('source_event_uri', '')
                }
            }
            output_content = json.dumps(output_data, indent=2, ensure_ascii=False)
        else:
            # Text format for easy copy-paste
            output_lines = []
            for i, tweet in enumerate(tweets, 1):
                output_lines.append(f"Tweet {i}:")
                output_lines.append(tweet)
                output_lines.append("")  # Empty line between tweets
            output_content = "\n".join(output_lines)
        
        # Output result
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"Twitter thread saved to: {args.output}", file=sys.stderr)
        else:
            print(output_content)
            
    except FileNotFoundError:
        print(f"Error: Article file '{args.article_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in article file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()