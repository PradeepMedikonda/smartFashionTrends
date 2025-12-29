"""
Test suite for the recommendation engine.
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.models import init_db, get_session, User, FashionItem, UserInteraction
from src.models.recommendation_engine import RecommendationEngine
from src.utils.data_generator import generate_sample_items, generate_sample_users, generate_sample_interactions


class TestRecommendationEngine(unittest.TestCase):
    """Test cases for the recommendation engine."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database and sample data."""
        # Use in-memory SQLite for testing
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        init_db()
        
        # Generate test data
        generate_sample_items(50)
        generate_sample_users(10)
        generate_sample_interactions(200)
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = RecommendationEngine()
        self.session = get_session()
    
    def test_build_user_item_matrix(self):
        """Test building user-item interaction matrix."""
        matrix = self.engine._build_user_item_matrix()
        
        self.assertIsNotNone(matrix)
        self.assertGreater(len(matrix), 0)
        print(f"✓ User-item matrix shape: {matrix.shape}")
    
    def test_build_item_features_matrix(self):
        """Test building item features matrix."""
        matrix = self.engine._build_item_features_matrix()
        
        self.assertIsNotNone(matrix)
        self.assertGreater(len(matrix), 0)
        print(f"✓ Item features matrix shape: {matrix.shape}")
    
    def test_get_recommendations(self):
        """Test getting recommendations for a user."""
        # Get first user
        user = self.session.query(User).first()
        self.assertIsNotNone(user)
        
        # Get recommendations
        recommendations = self.engine.get_recommendations(user.id, top_n=10)
        
        self.assertIsNotNone(recommendations)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 10)
        
        if len(recommendations) > 0:
            print(f"✓ Generated {len(recommendations)} recommendations for user {user.id}")
            print(f"  Top recommendation: {recommendations[0]['name']}")
    
    def test_update_user_preferences(self):
        """Test updating user preferences."""
        user = self.session.query(User).first()
        item = self.session.query(FashionItem).first()
        
        interaction_data = {
            'item_id': item.id,
            'interaction_type': 'like',
            'rating': 4.5
        }
        
        self.engine.update_user_preferences(user.id, interaction_data)
        
        # Verify interaction was created
        interaction = self.session.query(UserInteraction).filter_by(
            user_id=user.id,
            item_id=item.id,
            interaction_type='like'
        ).first()
        
        self.assertIsNotNone(interaction)
        print(f"✓ User preference updated successfully")
    
    def test_collaborative_filtering(self):
        """Test collaborative filtering recommendations."""
        user = self.session.query(User).first()
        
        recommendations = self.engine._collaborative_filtering(user.id, top_n=5)
        
        self.assertIsInstance(recommendations, list)
        print(f"✓ Collaborative filtering returned {len(recommendations)} recommendations")
    
    def test_content_based_filtering(self):
        """Test content-based filtering recommendations."""
        user = self.session.query(User).first()
        
        recommendations = self.engine._content_based_filtering(user.id, top_n=5)
        
        self.assertIsInstance(recommendations, list)
        print(f"✓ Content-based filtering returned {len(recommendations)} recommendations")


if __name__ == '__main__':
    print("\nRunning Recommendation Engine Tests...")
    print("=" * 60)
    unittest.main(verbosity=2)
