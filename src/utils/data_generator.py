"""
Utility functions for data initialization and sample data generation.
"""
import random
from datetime import datetime, timedelta

from ..data.models import User, FashionItem, UserInteraction, get_session


# Sample data
CATEGORIES = ['dress', 'shirt', 'pants', 'shoes', 'accessories', 'jacket', 'skirt', 'sweater']
STYLES = ['casual', 'formal', 'sporty', 'bohemian', 'vintage', 'modern', 'classic', 'trendy']
COLORS = ['black', 'white', 'blue', 'red', 'green', 'yellow', 'pink', 'gray', 'brown', 'beige']
BRANDS = ['Zara', 'H&M', 'Nike', 'Adidas', 'Gucci', 'Prada', 'Forever21', 'Gap', 'Uniqlo', 'Mango']
SEASONS = ['spring', 'summer', 'fall', 'winter', 'all']
INTERACTION_TYPES = ['view', 'like', 'cart', 'wishlist', 'purchase']


def generate_sample_items(n=100):
    """Generate sample fashion items."""
    # Get a fresh session after database initialization
    from ..data.models import get_session as _get_session
    session = _get_session()
    
    items = []
    for i in range(n):
        category = random.choice(CATEGORIES)
        style = random.choice(STYLES)
        color = random.choice(COLORS)
        brand = random.choice(BRANDS)
        season = random.choice(SEASONS)
        
        item = FashionItem(
            name=f"{style.capitalize()} {color.capitalize()} {category.capitalize()} {i+1}",
            category=category,
            subcategory=f"{category}_sub",
            brand=brand,
            price=round(random.uniform(20, 500), 2),
            color=color,
            style=style,
            season=season,
            description=f"A beautiful {style} {color} {category} from {brand}",
            image_url=f"https://example.com/images/{category}_{i+1}.jpg",
            trending_score=random.uniform(0, 1)
        )
        items.append(item)
        session.add(item)
    
    session.commit()
    print(f"Generated {n} sample fashion items")
    return items


def generate_sample_users(n=20):
    """Generate sample users."""
    from ..data.models import get_session as _get_session
    session = _get_session()
    
    users = []
    for i in range(n):
        user = User(
            username=f"user{i+1}",
            email=f"user{i+1}@example.com"
        )
        user.set_password("password123")
        users.append(user)
        session.add(user)
    
    session.commit()
    print(f"Generated {n} sample users")
    return users


def generate_sample_interactions(n_interactions=500):
    """Generate sample user interactions."""
    from ..data.models import get_session as _get_session
    session = _get_session()
    
    users = session.query(User).all()
    items = session.query(FashionItem).all()
    
    if not users or not items:
        print("No users or items found. Generate them first.")
        return
    
    interactions = []
    for _ in range(n_interactions):
        user = random.choice(users)
        item = random.choice(items)
        interaction_type = random.choice(INTERACTION_TYPES)
        
        # Generate timestamp in the last 60 days
        days_ago = random.randint(0, 60)
        timestamp = datetime.utcnow() - timedelta(days=days_ago)
        
        # Rating is optional, more likely for purchases and likes
        rating = None
        if interaction_type in ['purchase', 'like'] and random.random() > 0.5:
            rating = random.uniform(3.0, 5.0)
        
        interaction = UserInteraction(
            user_id=user.id,
            item_id=item.id,
            interaction_type=interaction_type,
            rating=rating,
            timestamp=timestamp
        )
        interactions.append(interaction)
        session.add(interaction)
    
    session.commit()
    print(f"Generated {n_interactions} sample interactions")
    return interactions


def initialize_sample_data():
    """Initialize database with sample data."""
    print("Initializing sample data...")
    
    # Generate sample data
    generate_sample_items(100)
    generate_sample_users(20)
    generate_sample_interactions(500)
    
    print("Sample data initialization complete!")


def clear_all_data():
    """Clear all data from database (use with caution!)."""
    session = get_session()
    
    session.query(UserInteraction).delete()
    session.query(FashionItem).delete()
    session.query(User).delete()
    
    session.commit()
    print("All data cleared from database")


if __name__ == '__main__':
    initialize_sample_data()
