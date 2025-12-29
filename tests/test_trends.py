"""
Test suite for the trend analyzer.
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment before imports
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from src.data.models import init_db
from src.models.trend_analyzer import TrendAnalyzer
from src.utils.data_generator import generate_sample_items, generate_sample_users, generate_sample_interactions


class TestTrendAnalyzer(unittest.TestCase):
    """Test cases for the trend analyzer."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database and sample data."""
        # Initialize database
        init_db()
        
        # Generate test data
        generate_sample_items(50)
        generate_sample_users(10)
        generate_sample_interactions(200)
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = TrendAnalyzer()
    
    def test_analyze_trends(self):
        """Test trend analysis."""
        trends = self.analyzer.analyze_trends(days=30)
        
        self.assertIsNotNone(trends)
        self.assertIn('by_category', trends)
        self.assertIn('by_style', trends)
        self.assertIn('by_color', trends)
        self.assertIn('by_brand', trends)
        self.assertIn('top_items', trends)
        
        print(f"✓ Trend analysis complete")
        print(f"  Categories: {len(trends['by_category'])}")
        print(f"  Styles: {len(trends['by_style'])}")
        print(f"  Top items: {len(trends['top_items'])}")
    
    def test_analyze_by_category(self):
        """Test category trend analysis."""
        trends = self.analyzer.analyze_trends(days=30)
        category_trends = trends['by_category']
        
        self.assertIsInstance(category_trends, list)
        if len(category_trends) > 0:
            trend = category_trends[0]
            self.assertIn('category', trend)
            self.assertIn('interaction_count', trend)
            self.assertIn('trend_score', trend)
            print(f"✓ Top trending category: {trend['category']}")
    
    def test_update_trending_scores(self):
        """Test updating trending scores."""
        self.analyzer.update_trending_scores()
        
        from src.data.models import FashionItem, get_session
        session = get_session()
        
        # Check that some items have trending scores
        trending_items = session.query(FashionItem).filter(
            FashionItem.trending_score > 0
        ).all()
        
        self.assertGreater(len(trending_items), 0)
        print(f"✓ Updated trending scores for {len(trending_items)} items")
    
    def test_get_seasonal_trends(self):
        """Test seasonal trend analysis."""
        seasonal_trends = self.analyzer.get_seasonal_trends('summer')
        
        self.assertIsInstance(seasonal_trends, list)
        print(f"✓ Found {len(seasonal_trends)} summer trends")


if __name__ == '__main__':
    print("\nRunning Trend Analyzer Tests...")
    print("=" * 60)
    unittest.main(verbosity=2)
