"""
Database models for the Smart Fashion Trends application.
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import bcrypt
import os

Base = declarative_base()


class User(Base):
    """User model for authentication and personalization."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    preferences = relationship('UserPreference', back_populates='user', cascade='all, delete-orphan')
    interactions = relationship('UserInteraction', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify user password."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


class FashionItem(Base):
    """Fashion item model representing products."""
    __tablename__ = 'fashion_items'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # e.g., 'dress', 'shoes', 'accessories'
    subcategory = Column(String(50))
    brand = Column(String(100))
    price = Column(Float)
    color = Column(String(50))
    style = Column(String(100))  # e.g., 'casual', 'formal', 'sporty'
    season = Column(String(20))  # e.g., 'spring', 'summer', 'fall', 'winter'
    description = Column(Text)
    image_url = Column(String(500))
    trending_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    interactions = relationship('UserInteraction', back_populates='item')


class UserPreference(Base):
    """User preference model for storing user taste and preferences."""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    preference_key = Column(String(50), nullable=False)  # e.g., 'favorite_category', 'preferred_style'
    preference_value = Column(String(200), nullable=False)
    weight = Column(Float, default=1.0)  # Importance weight
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='preferences')


class UserInteraction(Base):
    """User interaction model for tracking user behavior."""
    __tablename__ = 'user_interactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('fashion_items.id'), nullable=False)
    interaction_type = Column(String(20), nullable=False)  # 'view', 'like', 'purchase', 'cart', 'wishlist'
    rating = Column(Float)  # Optional rating 1-5
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='interactions')
    item = relationship('FashionItem', back_populates='interactions')


# Database initialization
def init_db(database_url=None):
    """Initialize the database."""
    if database_url is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///fashion_trends.db')
    
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return Session()


def get_session(database_url=None):
    """Get a database session."""
    if database_url is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///fashion_trends.db')
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session()
