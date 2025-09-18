"""
Bitcoin Mining News Twitter Bot
-------------------------------
This bot fetches the latest Bitcoin mining news from EventRegistry (NewsAPI.ai)
and posts them to Twitter/X as threaded tweets.
"""

import os
import json
import time
import logging
import random
from datetime import datetime as dt, timedelta

import tweepy
from eventregistry import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('bitcoin_mining_bot')

class BitcoinMiningNewsBot:
    def __init__(self):
        # Load API credentials
        self.twitter_client = self._init_twitter_client()
        self.er_client = self._init_eventregistry_client()
        
        # Load history of posted articles
        self.posted_articles = self._load_posted_articles()
        logger.info(f"Loaded {len(self.posted_articles['posted_uris'])} previously posted articles")
        
    def _init_twitter_client(self):
        """Initialize Twitter API client with OAuth 1.0a"""
        try:
            client = tweepy.Client(
                consumer_key=os.environ.get("TWITTER_API_KEY"),
                consumer_secret=os.environ.get("TWITTER_API_SECRET"),
                access_token=os.environ.get("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
            )
            logger.info("Twitter client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {str(e)}")
            raise

    def _init_eventregistry_client(self):
        """Initialize EventRegistry API client"""
        try:
            er = EventRegistry(apiKey=os.environ.get("EVENTREGISTRY_API_KEY"))
            logger.info("EventRegistry client initialized successfully")
            return er
        except Exception as e:
            logger.error(f"Failed to initialize EventRegistry client: {str(e)}")
            raise

    def _load_posted_articles(self):
        """Load the list of already posted article URIs"""
        try:
            with open("posted_articles.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("No existing posted articles file found, creating new one")
            return {"posted_uris": []}

    def _save_posted_articles(self):
        """Save the list of posted article URIs"""
        with open("posted_articles.json", "w") as f:
            json.dump(self.posted_articles, f, indent=2)
        logger.info(f"Saved {len(self.posted_articles['posted_uris'])} posted article URIs")

    def fetch_bitcoin_mining_articles(self, max_articles=10):
        """Fetch latest articles about Bitcoin mining"""
        try:
            logger.info("Fetching Bitcoin mining articles...")
            
            # Create a query for articles about Bitcoin mining
            q = QueryArticles(
                keywords=QueryItems.OR(["Bitcoin mining", "crypto mining", "cryptocurrency mining"]),
                conceptUri=QueryItems.OR([
                    self.er_client.getConceptUri("Bitcoin"),
                    self.er_client.getConceptUri("Mining"),
                    self.er_client.getConceptUri("Cryptocurrency")
                ]),
                dataType=["news"],
                lang="eng"
            )
            
            # Set time limit to recent articles (last 24 hours)
            current_date = dt.now()
            yesterday = current_date - timedelta(days=1)
            q.setDateLimit(yesterday, current_date)
            
            # Request article information
            q.setRequestedResult(
                RequestArticlesInfo(
                    page=1,
                    count=max_articles,
                    sortBy="date",
                    sortByAsc=False,
                    returnInfo=ReturnInfo(
                        articleInfo=ArticleInfoFlags(
                            duplicateList=False,
                            concepts=True,
                            categories=True,
                            image=True,
                            title=True,
                            body=True,
                            sentiment=True
                        )
                    )
                )
            )
            
            # Execute the query
            result = self.er_client.execQuery(q)
            
            if "articles" in result and "results" in result["articles"]:
                articles = result["articles"]["results"]
                logger.info(f"Found {len(articles)} articles about Bitcoin mining")
                return articles
            else:
                logger.warning("No articles found or unexpected response format")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching articles: {str(e)}")
            return []

    def create_tweet_text(self, article):
        """Create catchy tweet text for the article"""
        try:
            # Choose a catchy prefix
            prefixes = ["BREAKING: ", "JUST IN: ", "ALERT: ", "NEWS: ", "UPDATE: "]
            prefix = random.choice(prefixes)
            
            # Create a summary (use article title if it's concise enough)
            title = article.get("title", "").strip()
            
            # Clean up and shorten the title if needed
            if len(title) <= 240:  # Leave some room for the prefix
                summary = title
            else:
                # Take first sentence or truncate
                first_period = title.find(".")
                if first_period > 0 and first_period < 240:
                    summary = title[:first_period+1]
                else:
                    summary = title[:240] + "..."
            
            # Create the tweet text with the prefix
            tweet_text = f"{prefix}{summary}"
            
            # Truncate if too long for Twitter (280 character limit)
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:277] + "..."
            
            return tweet_text
            
        except Exception as e:
            logger.error(f"Error creating tweet text: {str(e)}")
            # Return a fallback tweet text
            return "New Bitcoin mining article: " + article.get("title", "")[:240]

    def post_to_twitter(self, article):
        """Post article as a thread on Twitter"""
        try:
            # Create the first tweet with a catchy summary
            tweet_text = self.create_tweet_text(article)
            logger.info(f"Posting tweet: {tweet_text[:50]}...")
            
            # Post the first tweet
            first_tweet = self.twitter_client.create_tweet(text=tweet_text)
            first_tweet_id = first_tweet.data["id"]
            logger.info(f"Posted first tweet with ID: {first_tweet_id}")
            
            # Create the second tweet with the article link
            article_url = article.get("url", "")
            if article_url:
                # Post as a reply to create a thread
                second_tweet = self.twitter_client.create_tweet(
                    text=f"Read more: {article_url}",
                    in_reply_to_tweet_id=first_tweet_id
                )
                logger.info(f"Posted second tweet (reply) with link to article")
            
            return first_tweet_id
            
        except Exception as e:
            logger.error(f"Error posting to Twitter: {str(e)}")
            return None

    def run(self):
        """Main function to run the bot"""
        try:
            logger.info("Starting Bitcoin Mining News Bot")
            
            # Fetch recent Bitcoin mining articles
            articles = self.fetch_bitcoin_mining_articles()
            
            # Track if we posted anything
            posted_count = 0
            
            # Process each article
            for article in articles:
                article_uri = article.get("uri")
                
                # Skip if we've already posted this article
                if article_uri in self.posted_articles["posted_uris"]:
                    logger.info(f"Skipping already posted article: {article.get('title')[:50]}...")
                    continue
                
                # Post to Twitter
                tweet_id = self.post_to_twitter(article)
                
                if tweet_id:
                    # Add to posted articles
                    self.posted_articles["posted_uris"].append(article_uri)
                    posted_count += 1
                    
                    # Only post one article per run to avoid flooding
                    logger.info(f"Posted article: {article.get('title')[:50]}...")
                    break
            
            # Save the updated list of posted articles
            self._save_posted_articles()
            
            if posted_count == 0:
                logger.info("No new articles to post")
            else:
                logger.info(f"Posted {posted_count} new articles")
                
        except Exception as e:
            logger.error(f"Error running bot: {str(e)}")


if __name__ == "__main__":
    bot = BitcoinMiningNewsBot()
    bot.run()
