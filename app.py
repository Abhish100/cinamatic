from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import requests
import os
import logging
from dotenv import load_dotenv
import json
import time
from functools import wraps
import random

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# API Keys
TRAKT_CLIENT_ID = os.getenv('TRAKT_CLIENT_ID')
TRAKT_CLIENT_SECRET = os.getenv('TRAKT_CLIENT_SECRET')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
WATCHMODE_API_KEY = os.getenv('WATCHMODE_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# Rate limiting
RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        current_time = time.time()
        
        if client_ip not in RATE_LIMIT:
            RATE_LIMIT[client_ip] = {'requests': [], 'blocked_until': 0}
        
        # Clean old requests
        RATE_LIMIT[client_ip]['requests'] = [
            req_time for req_time in RATE_LIMIT[client_ip]['requests']
            if current_time - req_time < RATE_LIMIT_WINDOW
        ]
        
        # Check if blocked
        if current_time < RATE_LIMIT[client_ip]['blocked_until']:
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # Check rate limit
        if len(RATE_LIMIT[client_ip]['requests']) >= RATE_LIMIT_MAX_REQUESTS:
            RATE_LIMIT[client_ip]['blocked_until'] = current_time + 60
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        RATE_LIMIT[client_ip]['requests'].append(current_time)
        return f(*args, **kwargs)
    return decorated_function

# Personality mapping system
PERSONALITY_MAPPING = {
    'quiet_night': ['drama', 'romance', 'indie'],
    'wild_party': ['comedy', 'action', 'adventure'],
    'puzzle_solving': ['mystery', 'thriller', 'sci-fi'],
    'adventure_seeker': ['adventure', 'fantasy', 'action'],
    'history_researcher': ['drama', 'biography', 'historical'],
    'skeptic': ['thriller', 'mystery', 'horror'],
    'creative_artist': ['drama', 'indie', 'romance'],
    'social_butterfly': ['comedy', 'romance', 'drama'],
    'tech_enthusiast': ['sci-fi', 'thriller', 'action'],
    'nature_lover': ['adventure', 'drama', 'documentary'],
    'bookworm': ['drama', 'biography', 'historical'],
    'fitness_freak': ['action', 'sports', 'adventure'],
    'foodie': ['comedy', 'drama', 'documentary'],
    'traveler': ['adventure', 'drama', 'documentary'],
    'gamer': ['sci-fi', 'action', 'fantasy'],
    'meditation': ['drama', 'indie', 'documentary'],
    'karaoke': ['comedy', 'musical', 'romance'],
    'board_games': ['mystery', 'thriller', 'comedy'],
    'movie_theater': ['drama', 'action', 'comedy'],
    'netflix': ['romance', 'drama', 'comedy']
}

@app.route('/')
@rate_limit
def index():
    """Landing page with cinematic design"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return render_template('error.html', error="Something went wrong"), 500

@app.route('/quiz')
@rate_limit
def quiz():
    """Personality quiz page"""
    try:
        return render_template('quiz.html')
    except Exception as e:
        logger.error(f"Error rendering quiz: {e}")
        return render_template('error.html', error="Something went wrong"), 500

@app.route('/process_quiz', methods=['POST'])
@rate_limit
def process_quiz():
    """Process quiz answers and calculate personality profile"""
    try:
        answers = request.form.to_dict()
        
        if not answers:
            return redirect(url_for('quiz'))
        
        # Calculate personality traits based on answers
        personality_traits = []
        for question, answer in answers.items():
            if answer in PERSONALITY_MAPPING:
                personality_traits.extend(PERSONALITY_MAPPING[answer])
        
        # Count most common traits
        trait_counts = {}
        for trait in personality_traits:
            trait_counts[trait] = trait_counts.get(trait, 0) + 1
        
        # Get top 3 dominant traits
        dominant_traits = sorted(trait_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        dominant_genres = [trait[0] for trait in dominant_traits]
        
        # Determine personality profile name and description
        personality_profile = get_personality_profile(dominant_genres, answers)
        
        # Store in session for recommendations
        session['personality_profile'] = {
            'traits': dominant_genres,
            'answers': answers,
            'profile_name': personality_profile['name'],
            'profile_description': personality_profile['description']
        }
        
        logger.info(f"Quiz completed - Profile: {personality_profile['name']}")
        return redirect(url_for('recommendations'))
        
    except Exception as e:
        logger.error(f"Error processing quiz: {e}")
        return render_template('error.html', error="Failed to process quiz"), 500

@app.route('/recommendations')
@rate_limit
def recommendations():
    """Display movie recommendations based on personality"""
    try:
        if 'personality_profile' not in session:
            return redirect(url_for('quiz'))
        
        profile = session['personality_profile']
        traits = profile['traits']
        
        # Get movie recommendations from Trakt API
        movies = get_movie_recommendations(traits)
        
        if not movies:
            # Fallback to mock data
            movies = get_mock_movies()
            logger.warning("Using mock data due to API failure")
        
        # Enrich with streaming data and news
        enriched_movies = enrich_movie_data(movies)
        
        return render_template('recommendations.html', 
                               movies=enriched_movies, 
                               personality_profile=profile)
                                
    except Exception as e:
        logger.error(f"Error rendering recommendations: {e}")
        return render_template('error.html', error="Failed to load recommendations"), 500

@app.route('/api/movies/<genre>')
@rate_limit
def api_movies(genre):
    """API endpoint for getting movies by genre"""
    try:
        movies = get_movie_recommendations([genre])
        return jsonify({'movies': movies})
    except Exception as e:
        logger.error(f"API error for genre {genre}: {e}")
        return jsonify({'error': 'Failed to fetch movies'}), 500

@app.route('/api/streaming/<movie_title>')
@rate_limit
def api_streaming(movie_title):
    """API endpoint for getting streaming info"""
    try:
        streaming_info = get_streaming_info(movie_title)
        return jsonify({'streaming': streaming_info})
    except Exception as e:
        logger.error(f"API error for streaming {movie_title}: {e}")
        return jsonify({'error': 'Failed to fetch streaming info'}), 500

@app.route('/api/trailer/<movie_title>')
@rate_limit
def api_trailer(movie_title):
    """API endpoint for getting movie trailer"""
    try:
        trailer_info = get_movie_trailer(movie_title)
        return jsonify({'trailer': trailer_info})
    except Exception as e:
        logger.error(f"API error for trailer {movie_title}: {e}")
        return jsonify({'error': 'Failed to fetch trailer'}), 500

@app.route('/new-movies')
@rate_limit
def new_movies():
    """Display latest movie releases"""
    try:
        # Get recent movies from Trakt API
        movies = get_new_movies()
        
        if not movies:
            # Fallback to mock data
            movies = get_mock_new_movies()
            logger.warning("Using mock data for new movies due to API failure")
        
        # Enrich with streaming data
        enriched_movies = enrich_movie_data(movies)
        
        return render_template('new_movies.html', movies=enriched_movies)
        
    except Exception as e:
        logger.error(f"Error rendering new movies: {e}")
        return render_template('error.html', error="Failed to load new movies"), 500

@app.route('/search')
@rate_limit
def search():
    """Search movies page"""
    try:
        query = request.args.get('q', '')
        if query:
            movies = search_movies(query)
            return render_template('search_results.html', movies=movies, query=query)
        return render_template('search.html')
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return render_template('error.html', error="Search failed"), 500

@app.route('/api/search/<query>')
@rate_limit
def api_search(query):
    """API endpoint for movie search"""
    try:
        movies = search_movies(query)
        return jsonify({'movies': movies, 'query': query})
    except Exception as e:
        logger.error(f"API error for search {query}: {e}")
        return jsonify({'error': 'Failed to search movies'}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

def get_movie_recommendations(genres):
    """Fetch movie recommendations from Trakt API"""
    if not TRAKT_CLIENT_ID:
        logger.warning("No Trakt API key provided, using mock data")
        return get_mock_movies()
    
    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version': '2',
        'trakt-api-key': TRAKT_CLIENT_ID
    }
    
    movies = []
    
    # Get trending movies first
    try:
        url = 'https://api.trakt.tv/movies/trending'
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for movie in data[:20]:  # Get top 20 trending movies
                movie_info = movie['movie']
                # Assign genres based on personality traits
                assigned_genre = genres[0] if genres else 'drama'
                movies.append({
                    'title': movie_info['title'],
                    'year': movie_info['year'],
                    'ids': movie_info['ids'],
                    'genre': assigned_genre,
                    'watchers': movie.get('watchers', 0)
                })
        else:
            logger.warning(f"Trakt API returned status {response.status_code}")
            # Try alternative endpoint
            url = 'https://api.trakt.tv/movies/popular'
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for movie in data[:15]:
                    movie_info = movie
                    assigned_genre = genres[0] if genres else 'drama'
                    movies.append({
                        'title': movie_info['title'],
                        'year': movie_info['year'],
                        'ids': movie_info['ids'],
                        'genre': assigned_genre,
                        'watchers': 0
                    })
            else:
                logger.warning(f"Trakt API popular movies returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching trending movies: {e}")
    
    # If we still don't have enough movies, try different endpoints
    if len(movies) < 10:
        try:
            # Try recent releases
            url = 'https://api.trakt.tv/movies/releases'
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for release in data[:10]:
                    movie_info = release['movie']
                    assigned_genre = genres[0] if genres else 'drama'
                    movies.append({
                        'title': movie_info['title'],
                        'year': movie_info['year'],
                        'ids': movie_info['ids'],
                        'genre': assigned_genre,
                        'watchers': 0
                    })
            else:
                logger.warning(f"Trakt API releases returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching releases: {e}")
    
    # If still no movies, use mock data
    if not movies:
        logger.warning("No movies fetched from Trakt API, using mock data")
        return get_mock_movies()
    
    return movies[:15]  # Return top 15 movies

def enrich_movie_data(movies):
    """Enrich movie data with streaming info and news"""
    enriched = []
    
    for movie in movies:
        try:
            # Add streaming data from WatchMode
            streaming_info = get_streaming_info(movie['title'])
            movie['streaming'] = streaming_info
            
            # Add news for top movies
            if len(enriched) < 3:  # Only for top 3
                news = get_movie_news(movie['title'])
                movie['news'] = news
            
            enriched.append(movie)
        except Exception as e:
            logger.error(f"Error enriching movie {movie['title']}: {e}")
            # Add default streaming info
            movie['streaming'] = {'netflix': True, 'hulu': False, 'prime': True}
            movie['news'] = []
            enriched.append(movie)
    
    return enriched

def get_streaming_info(movie_title):
    """Get streaming availability from WatchMode API"""
    if not WATCHMODE_API_KEY:
        return {'netflix': True, 'hulu': False, 'prime': True}
    
    try:
        # Search for the movie
        url = 'https://api.watchmode.com/v1/search'
        params = {
            'searchField': 'name',
            'searchValue': movie_title,
            'apiKey': WATCHMODE_API_KEY,
            'searchType': 'movie'
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('title_results') and len(data['title_results']) > 0:
                movie_id = data['title_results'][0]['id']
                
                # Get streaming sources
                sources_url = f'https://api.watchmode.com/v1/title/{movie_id}/sources'
                sources_response = requests.get(sources_url, params={'apiKey': WATCHMODE_API_KEY}, timeout=10)
                
                if sources_response.status_code == 200:
                    sources = sources_response.json()
                    streaming = {}
                    
                    # Map common streaming services
                    service_mapping = {
                        'netflix': 'netflix',
                        'hulu': 'hulu',
                        'amazon prime': 'prime',
                        'amazon prime video': 'prime',
                        'disney+': 'disney',
                        'hbo max': 'hbo',
                        'apple tv+': 'apple',
                        'peacock': 'peacock',
                        'paramount+': 'paramount'
                    }
                    
                    for source in sources:
                        if source['type'] == 'sub':
                            service_name = source['name'].lower()
                            for key, value in service_mapping.items():
                                if key in service_name:
                                    streaming[value] = True
                                    break
                    
                    # If no specific services found, provide default options
                    if not streaming:
                        streaming = {'netflix': True, 'hulu': False, 'prime': True}
                    
                    return streaming
                else:
                    logger.warning(f"WatchMode sources API returned status {sources_response.status_code}")
            else:
                logger.warning(f"No title results found for {movie_title}")
        else:
            logger.warning(f"WatchMode search API returned status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching streaming info for {movie_title}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in get_streaming_info: {e}")
    
    # Return default streaming options
    return {'netflix': True, 'hulu': False, 'prime': True}

def get_movie_news(movie_title):
    """Get recent news about the movie from NewsAPI"""
    if not NEWS_API_KEY:
        return []
    
    try:
        # Try different search queries for better results
        search_queries = [
            f'"{movie_title}" movie',
            f'"{movie_title}" film',
            f'"{movie_title}" cinema',
            f'"{movie_title}"'
        ]
        
        for query in search_queries:
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': query,
                'apiKey': NEWS_API_KEY,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 3,
                'domains': 'variety.com,hollywoodreporter.com,indiewire.com,deadline.com,thewrap.com'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                if articles:
                    return articles
            else:
                logger.warning(f"NewsAPI returned status {response.status_code} for query: {query}")
                
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in get_movie_news: {e}")
    
    return []

def get_personality_profile(genres, answers):
    """Determine personality profile based on quiz answers"""
    profiles = {
        'The Intrepid Explorer': {
            'genres': ['adventure', 'action', 'fantasy'],
            'description': 'You crave excitement and discovery. Your adventurous spirit draws you to epic journeys, thrilling action sequences, and fantastical worlds that push the boundaries of imagination.'
        },
        'The Thoughtful Analyst': {
            'genres': ['mystery', 'thriller', 'sci-fi'],
            'description': 'Your sharp mind loves to solve puzzles and explore complex narratives. You appreciate films that challenge your intellect and keep you guessing until the very end.'
        },
        'The Romantic Dreamer': {
            'genres': ['romance', 'drama', 'indie'],
            'description': 'You have a deep appreciation for human connection and emotional storytelling. Your heart is drawn to films that explore love, relationships, and the beautiful complexity of human nature.'
        },
        'The Social Butterfly': {
            'genres': ['comedy', 'romance', 'drama'],
            'description': 'You love to laugh and connect with others. Your vibrant personality enjoys films that bring people together, whether through humor, romance, or compelling character dynamics.'
        },
        'The Creative Artist': {
            'genres': ['drama', 'indie', 'biography'],
            'description': 'You have an artistic soul that appreciates beautiful storytelling and authentic performances. You are drawn to films that showcase human creativity and the power of artistic expression.'
        },
        'The Tech Enthusiast': {
            'genres': ['sci-fi', 'thriller', 'action'],
            'description': 'You are fascinated by innovation and the future. Your forward-thinking nature loves films that explore technology, artificial intelligence, and the possibilities of tomorrow.'
        }
    }
    
    # Find the best matching profile
    best_match = None
    highest_score = 0
    
    for profile_name, profile_data in profiles.items():
        score = 0
        for genre in genres:
            if genre in profile_data['genres']:
                score += 1
        if score > highest_score:
            highest_score = score
            best_match = profile_name
    
    # Default to Thoughtful Analyst if no clear match
    if not best_match:
        best_match = 'The Thoughtful Analyst'
    
    return {
        'name': best_match,
        'description': profiles[best_match]['description']
    }

def get_movie_trailer(movie_title):
    """Get movie trailer from YouTube API"""
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        logger.warning("No YouTube API key provided")
        return {
            'url': None,
            'title': movie_title,
            'available': False
        }
    query = f"{movie_title} official trailer"
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "key": api_key,
        "type": "video",
        "maxResults": 1,
        "videoEmbeddable": "true"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items")
            if items:
                video_id = items[0]["id"]["videoId"]
                return {
                    'url': f"http://googleusercontent.com/youtube.com/8{video_id}",
                    'title': movie_title,
                    'available': True
                }
        logger.warning(f"No trailer found for {movie_title}")
        return {
            'url': None,
            'title': movie_title,
            'available': False
        }
    except Exception as e:
        logger.error(f"Error fetching trailer from YouTube: {e}")
        return {
            'url': None,
            'title': movie_title,
            'available': False
        }

def get_new_movies():
    """Fetch latest movie releases from Trakt API"""
    if not TRAKT_CLIENT_ID:
        logger.warning("No Trakt API key provided, using mock data")
        return get_mock_new_movies()
    
    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version': '2',
        'trakt-api-key': TRAKT_CLIENT_ID
    }
    
    movies = []
    
    try:
        # Try different endpoints for new movies
        endpoints = [
            'https://api.trakt.tv/movies/releases',
            'https://api.trakt.tv/movies/trending',
            'https://api.trakt.tv/movies/popular'
        ]
        
        for url in endpoints:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'releases' in url:
                        # Handle releases endpoint
                        for release in data[:15]:
                            movie_info = release['movie']
                            movies.append({
                                'title': movie_info['title'],
                                'year': movie_info['year'],
                                'ids': movie_info['ids'],
                                'genre': 'new_release',
                                'release_date': release.get('release_date', ''),
                                'country': release.get('country', 'US')
                            })
                    else:
                        # Handle trending/popular endpoints
                        for movie in data[:15]:
                            movie_info = movie['movie'] if 'movie' in movie else movie
                            movies.append({
                                'title': movie_info['title'],
                                'year': movie_info['year'],
                                'ids': movie_info['ids'],
                                'genre': 'new_release',
                                'release_date': '',
                                'country': 'US'
                            })
                    
                    if movies:
                        break  # If we got movies, stop trying other endpoints
                        
                else:
                    logger.warning(f"Trakt API {url} returned status {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching from {url}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error in get_new_movies: {e}")
    
    if not movies:
        logger.warning("No new movies fetched from Trakt API, using mock data")
        return get_mock_new_movies()
    
    return movies[:15]  # Return top 15 movies

def get_mock_new_movies():
    """Return mock new movie data"""
    return [
        {
            'title': 'Dune: Part Two',
            'year': 2024,
            'genre': 'sci-fi',
            'release_date': '2024-03-01',
            'country': 'US',
            'streaming': {'netflix': False, 'hulu': False, 'prime': True},
            'news': []
        },
        {
            'title': 'Poor Things',
            'year': 2024,
            'genre': 'drama',
            'release_date': '2024-01-26',
            'country': 'US',
            'streaming': {'netflix': False, 'hulu': True, 'prime': False},
            'news': []
        },
        {
            'title': 'The Zone of Interest',
            'year': 2024,
            'genre': 'drama',
            'release_date': '2024-02-02',
            'country': 'US',
            'streaming': {'netflix': False, 'hulu': False, 'prime': False},
            'news': []
        },
        {
            'title': 'Killers of the Flower Moon',
            'year': 2023,
            'genre': 'drama',
            'release_date': '2023-10-20',
            'country': 'US',
            'streaming': {'netflix': False, 'hulu': False, 'prime': True},
            'news': []
        },
        {
            'title': 'Oppenheimer',
            'year': 2023,
            'genre': 'drama',
            'release_date': '2023-07-21',
            'country': 'US',
            'streaming': {'netflix': False, 'hulu': False, 'prime': True},
            'news': []
        }
    ]

def search_movies(query):
    """Search movies using Trakt API"""
    if not TRAKT_CLIENT_ID:
        logger.warning("No Trakt API key provided, using mock search")
        return search_mock_movies(query)
    
    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version': '2',
        'trakt-api-key': TRAKT_CLIENT_ID
    }
    
    movies = []
    
    try:
        # Try search endpoint first
        url = 'https://api.trakt.tv/search/movie'
        params = {'query': query, 'limit': 20}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for item in data:
                movie_info = item['movie']
                movies.append({
                    'title': movie_info['title'],
                    'year': movie_info['year'],
                    'ids': movie_info['ids'],
                    'genre': 'search_result',
                    'score': item.get('score', 0)
                })
        else:
            logger.warning(f"Trakt API search returned status {response.status_code}")
            
            # If search fails, try to get popular movies and filter
            url = 'https://api.trakt.tv/movies/popular'
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                query_lower = query.lower()
                for movie in data:
                    movie_info = movie
                    if query_lower in movie_info['title'].lower():
                        movies.append({
                            'title': movie_info['title'],
                            'year': movie_info['year'],
                            'ids': movie_info['ids'],
                            'genre': 'search_result',
                            'score': 0
                        })
                        if len(movies) >= 10:
                            break
            else:
                logger.warning(f"Trakt API popular movies returned status {response.status_code}")
                
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching movies: {e}")
    
    if not movies:
        logger.warning("No search results from Trakt API, using mock search")
        return search_mock_movies(query)
    
    return movies

def search_mock_movies(query):
    """Mock search function"""
    all_movies = [
        {'title': 'Inception', 'year': 2010, 'genre': 'sci-fi'},
        {'title': 'The Dark Knight', 'year': 2008, 'genre': 'action'},
        {'title': 'Pulp Fiction', 'year': 1994, 'genre': 'crime'},
        {'title': 'Forrest Gump', 'year': 1994, 'genre': 'drama'},
        {'title': 'The Shawshank Redemption', 'year': 1994, 'genre': 'drama'},
        {'title': 'Fight Club', 'year': 1999, 'genre': 'drama'},
        {'title': 'The Matrix', 'year': 1999, 'genre': 'sci-fi'},
        {'title': 'Goodfellas', 'year': 1990, 'genre': 'crime'},
        {'title': 'The Silence of the Lambs', 'year': 1991, 'genre': 'thriller'},
        {'title': 'Schindler\'s List', 'year': 1993, 'genre': 'drama'}
    ]
    
    query_lower = query.lower()
    results = []
    for movie in all_movies:
        if query_lower in movie['title'].lower():
            results.append(movie)
    
    return results

def get_mock_movies():
    """Return mock movie data for testing"""
    return [
        {
            'title': 'Inception',
            'year': 2010,
            'genre': 'sci-fi',
            'streaming': {'netflix': True, 'hulu': False, 'prime': True},
            'news': []
        },
        {
            'title': 'The Shawshank Redemption',
            'year': 1994,
            'genre': 'drama',
            'streaming': {'netflix': True, 'hulu': True, 'prime': False},
            'news': []
        },
        {
            'title': 'The Dark Knight',
            'year': 2008,
            'genre': 'action',
            'streaming': {'netflix': False, 'hulu': True, 'prime': True},
            'news': []
        },
        {
            'title': 'Pulp Fiction',
            'year': 1994,
            'genre': 'crime',
            'streaming': {'netflix': True, 'hulu': False, 'prime': True},
            'news': []
        },
        {
            'title': 'Forrest Gump',
            'year': 1994,
            'genre': 'drama',
            'streaming': {'netflix': True, 'hulu': True, 'prime': True},
            'news': []
        }
    ]

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)