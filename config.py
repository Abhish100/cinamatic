import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    TRAKT_CLIENT_ID = os.getenv('TRAKT_CLIENT_ID')
    TRAKT_CLIENT_SECRET = os.getenv('TRAKT_CLIENT_SECRET')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    WATCHMODE_API_KEY = os.getenv('WATCHMODE_API_KEY')
    
    # Rate limiting
    RATE_LIMIT_WINDOW = 60  # seconds
    RATE_LIMIT_MAX_REQUESTS = 100
    
    # API timeouts
    REQUEST_TIMEOUT = 10
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production settings
    RATE_LIMIT_MAX_REQUESTS = 50  # More restrictive in production
    REQUEST_TIMEOUT = 15  # Longer timeout for production

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 