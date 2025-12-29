"""
Training script for the recommendation model.
Run this to train and save the recommendation model.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.models import init_db
from src.models.recommendation_engine import RecommendationEngine
from src.models.trend_analyzer import TrendAnalyzer
from src.utils.data_generator import initialize_sample_data


def train_model():
    """Train the recommendation model."""
    print("Starting model training...")
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    
    # Generate sample data if needed
    print("\n2. Checking for sample data...")
    from src.data.models import get_session, User
    session = get_session()
    user_count = session.query(User).count()
    
    if user_count == 0:
        print("No data found. Generating sample data...")
        initialize_sample_data()
    else:
        print(f"Found {user_count} users in database")
    
    # Train recommendation engine
    print("\n3. Training recommendation engine...")
    engine = RecommendationEngine()
    
    # Build matrices (this trains the model)
    print("   - Building user-item matrix...")
    engine._build_user_item_matrix()
    
    print("   - Building item features matrix...")
    engine._build_item_features_matrix()
    
    # Save the model
    print("\n4. Saving model...")
    engine.save_model()
    
    # Update trending scores
    print("\n5. Updating trending scores...")
    analyzer = TrendAnalyzer()
    analyzer.update_trending_scores()
    
    print("\n✓ Model training complete!")
    print("\nYou can now:")
    print("  - Start the API server: python src/api/app.py")
    print("  - Get recommendations using the API")
    print("  - Test the model: python tests/test_recommendations.py")


if __name__ == '__main__':
    train_model()
