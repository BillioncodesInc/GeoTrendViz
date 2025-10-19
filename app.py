import os
import json
import random
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, flash, redirect, url_for, has_request_context
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

# Twitter API credentials - check session first, then environment variables
def get_twitter_credentials():
    """Get Twitter credentials from session or environment variables."""
    # Only access session if we're in a request context
    if has_request_context():
        return {
            'api_key': session.get('TWITTER_API_KEY') or os.getenv('TWITTER_API_KEY'),
            'api_secret': session.get('TWITTER_API_SECRET') or os.getenv('TWITTER_API_SECRET'),
            'access_token': session.get('TWITTER_ACCESS_TOKEN') or os.getenv('TWITTER_ACCESS_TOKEN'),
            'access_token_secret': session.get('TWITTER_ACCESS_TOKEN_SECRET') or os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            'bearer_token': session.get('TWITTER_BEARER_TOKEN') or os.getenv('TWITTER_BEARER_TOKEN')
        }
    else:
        # During app initialization, only use environment variables
        return {
            'api_key': os.getenv('TWITTER_API_KEY'),
            'api_secret': os.getenv('TWITTER_API_SECRET'),
            'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
            'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            'bearer_token': os.getenv('TWITTER_BEARER_TOKEN')
        }

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# Validate Twitter credentials
def validate_twitter_credentials(creds=None):
    """Check if Twitter API credentials are configured."""
    if creds is None:
        creds = get_twitter_credentials()
    
    missing = []
    if not creds.get('api_key'):
        missing.append('TWITTER_API_KEY')
    if not creds.get('api_secret'):
        missing.append('TWITTER_API_SECRET')
    if not creds.get('access_token'):
        missing.append('TWITTER_ACCESS_TOKEN')
    if not creds.get('access_token_secret'):
        missing.append('TWITTER_ACCESS_TOKEN_SECRET')
    if not creds.get('bearer_token'):
        missing.append('TWITTER_BEARER_TOKEN')
    
    if missing:
        # Only log warning if we're checking the default credentials (not during request)
        if creds is None or not has_request_context():
            logger.warning(f"Missing Twitter API credentials: {', '.join(missing)}")
            logger.warning("Application will start but Twitter API features will not work.")
        return False
    return True

# Check credentials
TWITTER_CREDENTIALS_VALID = validate_twitter_credentials()

# Initialize Twitter API client (v2 only) if credentials are available
def get_twitter_client():
    """Get or create Twitter API client with current credentials."""
    creds = get_twitter_credentials()
    if not validate_twitter_credentials(creds):
        return None
    
    try:
        return tweepy.Client(
            bearer_token=creds['bearer_token'],
            consumer_key=creds['api_key'],
            consumer_secret=creds['api_secret'],
            access_token=creds['access_token'],
            access_token_secret=creds['access_token_secret']
        )
    except Exception as e:
        logger.error(f"Failed to initialize Twitter API client: {e}")
        return None

client = None
if TWITTER_CREDENTIALS_VALID:
    try:
        client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        logger.info("Twitter API client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Twitter API client: {e}")
        TWITTER_CREDENTIALS_VALID = False

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
    twitter_client = get_twitter_client()
    if twitter_client is None:
        logger.error("Twitter API credentials not configured")
        raise Exception("Twitter API is not configured. Please configure it in the settings page.")
    
    logger.info(f"Fetching trends for location: {location}, language: {lang}")
    try:
        # Search for recent tweets mentioning the location
        query = f"{location} -is:retweet lang:{lang}"
        tweets = twitter_client.search_recent_tweets(
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
    twitter_client = get_twitter_client()
    if twitter_client is None:
        logger.error("Twitter API credentials not configured")
        raise Exception("Twitter API is not configured. Please configure it in the settings page.")
    
    logger.info(f"Fetching tweets for query: {query}, language: {lang}")
    try:
        tweets = twitter_client.search_recent_tweets(
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
    twitter_client = get_twitter_client()
    if twitter_client is None:
        return jsonify({'error': 'Twitter API is not configured. Please configure it in the settings page.'}), 503
    
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
        tweets = twitter_client.search_recent_tweets(
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
def index():
    # Check if Twitter API is configured
    twitter_client = get_twitter_client()
    if twitter_client is None:
        # Show demo word cloud instead of error
        demo_words = {
            '#Technology': 1200,
            '#AI': 1000,
            '#Innovation': 900,
            '#DataScience': 850,
            '#MachineLearning': 800,
            '#Cloud': 750,
            '#Cybersecurity': 700,
            '#IoT': 650,
            '#Blockchain': 600,
            '#5G': 550,
            'trending': 500,
            'viral': 480,
            'breaking': 460,
            'news': 440,
            'update': 420,
            'latest': 400,
            'popular': 380,
            'hot': 360,
            'buzz': 340,
            'topic': 320
        }
        words_data, canvas_width, canvas_height = generate_wordcloud_layout(demo_words)
        return render_template('wordcloud.html',
                             display_name='Demo Trends',
                             words_data=words_data,
                             tweets_lookup=json.dumps({}),
                             canvas_width=canvas_width,
                             canvas_height=canvas_height,
                             languages=SUPPORTED_LANGUAGES,
                             selected_lang='en',
                             is_demo=True)
    
    if request.method == 'GET':
        # Fetch default US trends
        try:
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
        except Exception as e:
            logger.error(f"Error fetching default trends: {e}")
        
        # Show demo mode if API call fails
        demo_words = {
            '#Technology': 1200,
            '#AI': 1000,
            '#Innovation': 900,
            '#DataScience': 850,
            '#MachineLearning': 800,
            '#Cloud': 750,
            '#Cybersecurity': 700,
            '#IoT': 650,
            '#Blockchain': 600,
            '#5G': 550,
            'trending': 500,
            'viral': 480,
            'breaking': 460,
            'news': 440,
            'update': 420,
            'latest': 400,
            'popular': 380,
            'hot': 360,
            'buzz': 340,
            'topic': 320
        }
        words_data, canvas_width, canvas_height = generate_wordcloud_layout(demo_words)
        return render_template('wordcloud.html',
                             display_name='Demo Trends',
                             words_data=words_data,
                             tweets_lookup=json.dumps({}),
                             canvas_width=canvas_width,
                             canvas_height=canvas_height,
                             languages=SUPPORTED_LANGUAGES,
                             selected_lang='en',
                             is_demo=True)
    
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
            # Show demo mode instead of error
            demo_words = {
                '#Technology': 1200,
                '#AI': 1000,
                '#Innovation': 900,
                '#DataScience': 850,
                '#MachineLearning': 800,
                '#Cloud': 750,
                '#Cybersecurity': 700,
                '#IoT': 650,
                '#Blockchain': 600,
                '#5G': 550,
                'trending': 500,
                'viral': 480,
                'breaking': 460,
                'news': 440,
                'update': 420,
                'latest': 400,
                'popular': 380,
                'hot': 360,
                'buzz': 340,
                'topic': 320
            }
            words_data, canvas_width, canvas_height = generate_wordcloud_layout(demo_words)
            return render_template('wordcloud.html',
                                 display_name='Demo Trends',
                                 words_data=words_data,
                                 tweets_lookup=json.dumps({}),
                                 canvas_width=canvas_width,
                                 canvas_height=canvas_height,
                                 languages=SUPPORTED_LANGUAGES,
                                 selected_lang=lang,
                                 is_demo=True)
        
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
        # Show demo mode instead of error
        demo_words = {
            '#Technology': 1200,
            '#AI': 1000,
            '#Innovation': 900,
            '#DataScience': 850,
            '#MachineLearning': 800,
            '#Cloud': 750,
            '#Cybersecurity': 700,
            '#IoT': 650,
            '#Blockchain': 600,
            '#5G': 550,
            'trending': 500,
            'viral': 480,
            'breaking': 460,
            'news': 440,
            'update': 420,
            'latest': 400,
            'popular': 380,
            'hot': 360,
            'buzz': 340,
            'topic': 320
        }
        words_data, canvas_width, canvas_height = generate_wordcloud_layout(demo_words)
        return render_template('wordcloud.html',
                             display_name='Demo Trends',
                             words_data=words_data,
                             tweets_lookup=json.dumps({}),
                             canvas_width=canvas_width,
                             canvas_height=canvas_height,
                             languages=SUPPORTED_LANGUAGES,
                             selected_lang=lang,
                             is_demo=True)

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Configuration page for Twitter API credentials."""
    if request.method == 'POST':
        # Save credentials to session
        session['TWITTER_API_KEY'] = request.form.get('api_key', '').strip()
        session['TWITTER_API_SECRET'] = request.form.get('api_secret', '').strip()
        session['TWITTER_ACCESS_TOKEN'] = request.form.get('access_token', '').strip()
        session['TWITTER_ACCESS_TOKEN_SECRET'] = request.form.get('access_token_secret', '').strip()
        session['TWITTER_BEARER_TOKEN'] = request.form.get('bearer_token', '').strip()
        
        # Validate credentials
        creds = get_twitter_credentials()
        if validate_twitter_credentials(creds):
            # Test the credentials
            try:
                test_client = get_twitter_client()
                if test_client:
                    flash('Twitter API credentials saved and validated successfully!', 'success')
                    logger.info('Twitter API credentials configured via web interface')
                    return redirect(url_for('index'))
                else:
                    flash('Failed to initialize Twitter client. Please check your credentials.', 'error')
            except Exception as e:
                flash(f'Error validating credentials: {str(e)}', 'error')
                logger.error(f'Error validating credentials: {e}')
        else:
            flash('Please fill in all required fields.', 'error')
    
    # Get current configuration status
    creds = get_twitter_credentials()
    config_status = 'configured' if validate_twitter_credentials(creds) else 'not_configured'
    
    # Mask credentials for display (show only first/last few characters)
    current_config = {}
    if creds.get('api_key'):
        current_config['api_key'] = creds['api_key'][:8] + '...' if len(creds['api_key']) > 8 else ''
    if creds.get('api_secret'):
        current_config['api_secret'] = '***'
    if creds.get('access_token'):
        current_config['access_token'] = creds['access_token'][:8] + '...' if len(creds['access_token']) > 8 else ''
    if creds.get('access_token_secret'):
        current_config['access_token_secret'] = '***'
    if creds.get('bearer_token'):
        current_config['bearer_token'] = '***'
    
    return render_template('config.html',
                         config_status=config_status,
                         current_config=current_config)

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')

