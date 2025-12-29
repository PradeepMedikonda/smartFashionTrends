"""
Trend Analysis Model - Analyzes fashion trends based on user interactions and temporal patterns.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Dict

from ..data.models import FashionItem, UserInteraction, get_session


class TrendAnalyzer:
    """
    Analyzes fashion trends based on user behavior and temporal patterns.
    """
    
    def __init__(self):
        """Initialize the trend analyzer."""
        self.session = get_session()
    
    def analyze_trends(self, days: int = 30) -> Dict[str, List[Dict]]:
        """
        Analyze current fashion trends across different dimensions.
        
        Args:
            days: Number of days to look back for trend analysis
            
        Returns:
            Dictionary containing trends by category, style, color, etc.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get recent interactions
        recent_interactions = self.session.query(UserInteraction).filter(
            UserInteraction.timestamp >= cutoff_date
        ).all()
        
        # Collect item data from interactions
        item_ids = [i.item_id for i in recent_interactions]
        items = self.session.query(FashionItem).filter(FashionItem.id.in_(item_ids)).all()
        item_dict = {item.id: item for item in items}
        
        # Analyze by different dimensions
        trends = {
            'by_category': self._analyze_by_category(recent_interactions, item_dict),
            'by_style': self._analyze_by_style(recent_interactions, item_dict),
            'by_color': self._analyze_by_color(recent_interactions, item_dict),
            'by_brand': self._analyze_by_brand(recent_interactions, item_dict),
            'top_items': self._get_top_trending_items(recent_interactions, item_dict, top_n=20)
        }
        
        return trends
    
    def _analyze_by_category(self, interactions: List, item_dict: Dict) -> List[Dict]:
        """Analyze trends by category."""
        category_counts = Counter()
        category_scores = {}
        
        for interaction in interactions:
            item = item_dict.get(interaction.item_id)
            if item and item.category:
                weight = self._get_interaction_weight(interaction)
                category_counts[item.category] += 1
                category_scores[item.category] = category_scores.get(item.category, 0) + weight
        
        trends = []
        for category, count in category_counts.most_common(10):
            trends.append({
                'category': category,
                'interaction_count': count,
                'trend_score': category_scores[category],
                'growth_rate': self._calculate_growth_rate(category, 'category')
            })
        
        return trends
    
    def _analyze_by_style(self, interactions: List, item_dict: Dict) -> List[Dict]:
        """Analyze trends by style."""
        style_counts = Counter()
        style_scores = {}
        
        for interaction in interactions:
            item = item_dict.get(interaction.item_id)
            if item and item.style:
                weight = self._get_interaction_weight(interaction)
                style_counts[item.style] += 1
                style_scores[item.style] = style_scores.get(item.style, 0) + weight
        
        trends = []
        for style, count in style_counts.most_common(10):
            trends.append({
                'style': style,
                'interaction_count': count,
                'trend_score': style_scores[style],
                'growth_rate': self._calculate_growth_rate(style, 'style')
            })
        
        return trends
    
    def _analyze_by_color(self, interactions: List, item_dict: Dict) -> List[Dict]:
        """Analyze trends by color."""
        color_counts = Counter()
        color_scores = {}
        
        for interaction in interactions:
            item = item_dict.get(interaction.item_id)
            if item and item.color:
                weight = self._get_interaction_weight(interaction)
                color_counts[item.color] += 1
                color_scores[item.color] = color_scores.get(item.color, 0) + weight
        
        trends = []
        for color, count in color_counts.most_common(10):
            trends.append({
                'color': color,
                'interaction_count': count,
                'trend_score': color_scores[color]
            })
        
        return trends
    
    def _analyze_by_brand(self, interactions: List, item_dict: Dict) -> List[Dict]:
        """Analyze trends by brand."""
        brand_counts = Counter()
        brand_scores = {}
        
        for interaction in interactions:
            item = item_dict.get(interaction.item_id)
            if item and item.brand:
                weight = self._get_interaction_weight(interaction)
                brand_counts[item.brand] += 1
                brand_scores[item.brand] = brand_scores.get(item.brand, 0) + weight
        
        trends = []
        for brand, count in brand_counts.most_common(10):
            trends.append({
                'brand': brand,
                'interaction_count': count,
                'trend_score': brand_scores[brand]
            })
        
        return trends
    
    def _get_top_trending_items(self, interactions: List, item_dict: Dict, top_n: int = 20) -> List[Dict]:
        """Get top trending individual items."""
        item_scores = {}
        
        for interaction in interactions:
            item = item_dict.get(interaction.item_id)
            if item:
                weight = self._get_interaction_weight(interaction)
                if item.id not in item_scores:
                    item_scores[item.id] = {
                        'item': item,
                        'score': 0,
                        'interaction_count': 0
                    }
                item_scores[item.id]['score'] += weight
                item_scores[item.id]['interaction_count'] += 1
        
        # Sort by score
        sorted_items = sorted(item_scores.values(), key=lambda x: x['score'], reverse=True)
        
        trends = []
        for item_data in sorted_items[:top_n]:
            item = item_data['item']
            trends.append({
                'item_id': item.id,
                'name': item.name,
                'category': item.category,
                'brand': item.brand,
                'style': item.style,
                'price': item.price,
                'trend_score': item_data['score'],
                'interaction_count': item_data['interaction_count']
            })
        
        return trends
    
    def _get_interaction_weight(self, interaction) -> float:
        """Calculate weight for an interaction based on type and recency."""
        # Base weights by interaction type
        type_weights = {
            'view': 1.0,
            'like': 3.0,
            'cart': 4.0,
            'wishlist': 5.0,
            'purchase': 10.0
        }
        
        weight = type_weights.get(interaction.interaction_type, 1.0)
        
        # Apply rating multiplier if available
        if interaction.rating:
            weight *= interaction.rating / 5.0
        
        # Apply recency decay (more recent = higher weight)
        days_old = (datetime.utcnow() - interaction.timestamp).days
        recency_factor = 1.0 / (1.0 + days_old * 0.1)  # Decay factor
        weight *= recency_factor
        
        return weight
    
    def _calculate_growth_rate(self, value: str, dimension: str) -> float:
        """
        Calculate growth rate for a trend.
        Compares last 7 days vs previous 7 days.
        """
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)
        
        # Get recent week interactions
        recent_interactions = self.session.query(UserInteraction).filter(
            UserInteraction.timestamp >= week_ago
        ).all()
        
        # Get previous week interactions
        previous_interactions = self.session.query(UserInteraction).filter(
            UserInteraction.timestamp >= two_weeks_ago,
            UserInteraction.timestamp < week_ago
        ).all()
        
        # Count matches
        recent_count = 0
        previous_count = 0
        
        for interaction in recent_interactions:
            item = self.session.query(FashionItem).filter_by(id=interaction.item_id).first()
            if item and getattr(item, dimension, None) == value:
                recent_count += 1
        
        for interaction in previous_interactions:
            item = self.session.query(FashionItem).filter_by(id=interaction.item_id).first()
            if item and getattr(item, dimension, None) == value:
                previous_count += 1
        
        # Calculate growth rate
        if previous_count == 0:
            return 100.0 if recent_count > 0 else 0.0
        
        growth_rate = ((recent_count - previous_count) / previous_count) * 100
        return round(growth_rate, 2)
    
    def update_trending_scores(self):
        """
        Update trending scores for all items in the database.
        This should be run periodically (e.g., daily).
        """
        trends = self.analyze_trends(days=30)
        top_items = trends['top_items']
        
        # Reset all trending scores
        self.session.query(FashionItem).update({'trending_score': 0.0})
        
        # Update scores for trending items
        max_score = max([item['trend_score'] for item in top_items]) if top_items else 1.0
        
        for item_data in top_items:
            item = self.session.query(FashionItem).filter_by(id=item_data['item_id']).first()
            if item:
                # Normalize score to 0-1 range
                normalized_score = item_data['trend_score'] / max_score
                item.trending_score = normalized_score
        
        self.session.commit()
        print(f"Updated trending scores for {len(top_items)} items")
    
    def get_seasonal_trends(self, season: str) -> List[Dict]:
        """
        Get trends specific to a season.
        
        Args:
            season: Season name ('spring', 'summer', 'fall', 'winter')
        """
        items = self.session.query(FashionItem).filter_by(season=season).all()
        
        # Get interactions for seasonal items
        item_ids = [item.id for item in items]
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        interactions = self.session.query(UserInteraction).filter(
            UserInteraction.item_id.in_(item_ids),
            UserInteraction.timestamp >= cutoff_date
        ).all()
        
        item_dict = {item.id: item for item in items}
        
        return self._get_top_trending_items(interactions, item_dict, top_n=15)
