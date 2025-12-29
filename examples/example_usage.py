"""
Example usage of the Smart Fashion Trends recommendation system.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.models import init_db, get_session, User, FashionItem
from src.models.recommendation_engine import RecommendationEngine
from src.models.trend_analyzer import TrendAnalyzer


def example_usage():
    """Demonstrate how to use the recommendation system."""
    
    print("=" * 70)
    print("Smart Fashion Trends - Example Usage")
    print("=" * 70)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    session = get_session()
    
    # Check if we have data
    user_count = session.query(User).count()
    item_count = session.query(FashionItem).count()
    
    print(f"   Database has {user_count} users and {item_count} items")
    
    if user_count == 0:
        print("   No data found. Run 'python src/train_model.py' first!")
        return
    
    # Get a user
    user = session.query(User).first()
    print(f"\n2. Using user: {user.username} (ID: {user.id})")
    
    # Get recommendations
    print("\n3. Getting personalized recommendations...")
    engine = RecommendationEngine()
    recommendations = engine.get_recommendations(user.id, top_n=5)
    
    print(f"\n   Top 5 Recommendations for {user.username}:")
    print("   " + "-" * 66)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n   {i}. {rec['name']}")
        print(f"      Category: {rec['category']}")
        print(f"      Brand: {rec['brand']}")
        print(f"      Style: {rec['style']}")
        print(f"      Price: ${rec['price']:.2f}")
        print(f"      Recommendation Score: {rec['recommendation_score']:.3f}")
    
    # Simulate user interaction
    print("\n4. Simulating user interaction (liking an item)...")
    if recommendations:
        liked_item = recommendations[0]
        engine.update_user_preferences(user.id, {
            'item_id': liked_item['item_id'],
            'interaction_type': 'like',
            'rating': 5.0
        })
        print(f"   User liked: {liked_item['name']}")
    
    # Get trends
    print("\n5. Analyzing fashion trends...")
    analyzer = TrendAnalyzer()
    trends = analyzer.analyze_trends(days=30)
    
    print("\n   Trending Categories:")
    for i, trend in enumerate(trends['by_category'][:5], 1):
        print(f"   {i}. {trend['category']} (Score: {trend['trend_score']:.1f})")
    
    print("\n   Trending Styles:")
    for i, trend in enumerate(trends['by_style'][:5], 1):
        print(f"   {i}. {trend['style']} (Score: {trend['trend_score']:.1f})")
    
    print("\n   Top Trending Items:")
    for i, item in enumerate(trends['top_items'][:3], 1):
        print(f"   {i}. {item['name']}")
        print(f"      Brand: {item['brand']} | Price: ${item['price']:.2f}")
    
    # Get updated recommendations
    print("\n6. Getting updated recommendations after interaction...")
    new_recommendations = engine.get_recommendations(user.id, top_n=3)
    
    print(f"\n   Updated Recommendations:")
    for i, rec in enumerate(new_recommendations, 1):
        print(f"   {i}. {rec['name']} (Score: {rec['recommendation_score']:.3f})")
    
    print("\n" + "=" * 70)
    print("Example complete! The system is working correctly.")
    print("=" * 70)
    print("\nNext steps:")
    print("  - Start the API server: python src/api/app.py")
    print("  - Access API at: http://localhost:5000")
    print("  - Read API docs in README.md")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    example_usage()
