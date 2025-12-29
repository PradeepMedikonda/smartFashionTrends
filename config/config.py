"""
Configuration settings for the Smart Fashion Trends application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///fashion_trends.db')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/')
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Model parameters
    RECOMMENDATION_TOP_N = 10
    MIN_INTERACTIONS = 5
    SIMILARITY_THRESHOLD = 0.5
    
    # Training parameters
    BATCH_SIZE = 32
    EPOCHS = 50
    LEARNING_RATE = 0.001
    EMBEDDING_DIM = 50
    
    # Feature weights for content-based filtering
    FEATURE_WEIGHTS = {
        'category': 0.3,
        'style': 0.25,
        'color': 0.15,
        'brand': 0.15,
        'price_range': 0.1,
        'season': 0.05
    }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


# Select configuration based on environment
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

config = config_by_name[os.getenv('ENVIRONMENT', 'default')]
