import os
import json
import random
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, flash
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import tweepy
from wordcloud import WordCloud
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
log_handler = RotatingFileHandler('app.log', maxBytes=10485760, backupCount=5)  # 10MB per file, keep 5 backups
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        log_handler,
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24).hex())
csrf = CSRFProtect(app)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Twitter API credentials
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# Initialize Twitter API client (v2 only)
client = tweepy.Client(
    bearer_token=TWITTER_BEARER_TOKEN,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
)

# Supported languages with their codes and names
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'zh': 'Chinese',
    'ru': 'Russian'
}

def handle_api_error(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except tweepy.TweepyException as e:
            logger.error(f"Twitter API error: {str(e)}")
            return jsonify({'error': 'Twitter API error occurred'}), 500
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return jsonify({'error': 'An unexpected error occurred'}), 500
    return decorated_function

def validate_location(location):
    """Validate location input."""
    if not location or len(location.strip()) == 0:
        return False, "Location cannot be empty"
    if len(location) > 100:
        return False, "Location name is too long"
    return True, None

@handle_api_error
def fetch_top_trends_by_location(location, lang='en'):
    """Fetch top trends for a given location using v2 API."""
    logger.info(f"Fetching trends for location: {location}, language: {lang}")
    try:
        # Search for recent tweets mentioning the location
        query = f"{location} -is:retweet lang:{lang}"
        tweets = client.search_recent_tweets(
            query=query,
            max_results=100,
            tweet_fields=['created_at', 'text', 'public_metrics']
        )
        
        if not tweets.data:
            logger.warning(f"No tweets found for location: {location}")
            return []
        
        # Count occurrences of hashtags and keywords
        trend_counts = {}
        for tweet in tweets.data:
            # Extract hashtags and keywords
            words = tweet.text.lower().split()
            for word in words:
                if word.startswith('#'):
                    trend_counts[word] = trend_counts.get(word, 0) + tweet.public_metrics['retweet_count'] + 1
                elif len(word) > 3 and word != location.lower():
                    trend_counts[word] = trend_counts.get(word, 0) + 1
        
        # Sort by count and get top 20
        sorted_trends = sorted(trend_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        return [{'name': trend[0], 'tweet_volume': trend[1]} for trend in sorted_trends]
    except Exception as e:
        logger.error(f"Error fetching trends: {e}")
        raise

@handle_api_error
def fetch_top_5_recent_tweets(query, lang='en'):
    """Fetch top 5 recent tweets for a given query using v2 API."""
    logger.info(f"Fetching tweets for query: {query}, language: {lang}")
    try:
        tweets = client.search_recent_tweets(
            query=f"{query} -is:retweet lang:{lang}",
            max_results=10,
            tweet_fields=['created_at', 'text', 'public_metrics']
        )
        if not tweets.data:
            logger.warning(f"No tweets found for query: {query}")
            return []
        return [{
            'text': tweet.text,
            'url': f"https://twitter.com/user/status/{tweet.id}",
            'metrics': tweet.public_metrics,
            'created_at': tweet.created_at.isoformat()
        } for tweet in tweets.data]
    except Exception as e:
        logger.error(f"Error fetching tweets: {e}")
        raise

def generate_wordcloud_layout(frequencies, width=800, height=600):
    """Generate word cloud layout with font sizes, colors, tweet_volume, type, and random orientation."""
    wordcloud = WordCloud(
        width=width,
        height=height,
        background_color='white',
        prefer_horizontal=1.0
    ).generate_from_frequencies(frequencies)
    
    words_data = []
    for (word, freq), font_size, position, orientation, color in wordcloud.layout_:
        word_type = 'hashtag' if word.startswith('#') else 'keyword'
        word_orientation = random.choice(['horizontal', 'vertical'])
        words_data.append({
            'word': word,
            'font_size': int(font_size * 2),
            'color': f'#{random.randint(0, 0xFFFFFF):06x}',
            'tweet_volume': freq,
            'type': word_type,
            'orientation': word_orientation
        })
    return words_data, width, height

@app.route('/fetch_tweets', methods=['POST'])
@limiter.limit("30 per minute")
@handle_api_error
def fetch_tweets():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        word = data.get('word')
        lang = data.get('lang', 'en')
        
        if not word:
            return jsonify({'error': 'No word provided'}), 400
            
        logger.info(f"Fetching tweets for word: {word}, language: {lang}")
        
        # Fetch tweets using the v2 API
        tweets = client.search_recent_tweets(
            query=f"{word} -is:retweet lang:{lang}",
            max_results=10,
            tweet_fields=['created_at', 'text', 'public_metrics']
        )
        
        if not tweets.data:
            logger.warning(f"No tweets found for word: {word}")
            return jsonify({'tweets': []})
            
        # Process tweets
        processed_tweets = []
        for tweet in tweets.data:
            processed_tweets.append({
                'text': tweet.text,
                'url': f"https://twitter.com/user/status/{tweet.id}",
                'metrics': {
                    'retweet_count': tweet.public_metrics.get('retweet_count', 0),
                    'reply_count': tweet.public_metrics.get('reply_count', 0),
                    'like_count': tweet.public_metrics.get('like_count', 0)
                },
                'created_at': tweet.created_at.isoformat()
            })
            
        logger.info(f"Successfully fetched {len(processed_tweets)} tweets")
        return jsonify({'tweets': processed_tweets})
        
    except tweepy.TweepyException as e:
        logger.error(f"Twitter API error: {str(e)}")
        return jsonify({'error': 'Error fetching tweets from Twitter API'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("60 per minute")
@handle_api_error
def index():
    if request.method == 'GET':
        # Fetch default US trends
        trends = fetch_top_trends_by_location('USA', 'en')
        if trends:
            frequencies = {t['name']: t['tweet_volume'] for t in trends}
            words_data, canvas_width, canvas_height = generate_wordcloud_layout(frequencies)
            return render_template('wordcloud.html',
                                 display_name='USA',
                                 words_data=words_data,
                                 tweets_lookup=json.dumps({}),
                                 canvas_width=canvas_width,
                                 canvas_height=canvas_height,
                                 languages=SUPPORTED_LANGUAGES,
                                 selected_lang='en')
        return render_template('wordcloud.html', 
                             languages=SUPPORTED_LANGUAGES, 
                             selected_lang='en',
                             error="Could not fetch default trends")
    
    location = request.form.get('location', '').strip()
    lang = request.form.get('language', 'en')
    
    is_valid, error_msg = validate_location(location)
    if not is_valid:
        flash(error_msg, 'error')
        return render_template('wordcloud.html', 
                             error=error_msg,
                             languages=SUPPORTED_LANGUAGES,
                             selected_lang=lang)
    
    try:
        trends = fetch_top_trends_by_location(location, lang)
        if not trends:
            flash("Could not fetch trends for that location", 'error')
            return render_template('wordcloud.html', 
                                 error="Could not fetch trends for that location",
                                 languages=SUPPORTED_LANGUAGES,
                                 selected_lang=lang)
        
        frequencies = {t['name']: t['tweet_volume'] for t in trends}
        words_data, canvas_width, canvas_height = generate_wordcloud_layout(frequencies)
        return render_template('wordcloud.html',
                             display_name=location,
                             words_data=words_data,
                             tweets_lookup=json.dumps({}),
                             canvas_width=canvas_width,
                             canvas_height=canvas_height,
                             languages=SUPPORTED_LANGUAGES,
                             selected_lang=lang)
    
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        flash("An error occurred while processing your request", 'error')
        return render_template('wordcloud.html', 
                             error="An error occurred while processing your request",
                             languages=SUPPORTED_LANGUAGES,
                             selected_lang=lang)

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true') 