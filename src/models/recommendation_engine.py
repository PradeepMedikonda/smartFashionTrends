"""
Recommendation Engine - Core AI model for personalized fashion recommendations.
Uses hybrid approach: collaborative filtering + content-based filtering.
"""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import List, Dict, Tuple
import joblib
import os
from datetime import datetime, timedelta

from ..data.models import User, FashionItem, UserInteraction, UserPreference, get_session
from config.config import config


class RecommendationEngine:
    """
    Hybrid recommendation engine combining collaborative and content-based filtering.
    Trained per user to provide personalized recommendations.
    """
    
    def __init__(self, model_path=None):
        """Initialize the recommendation engine."""
        self.model_path = model_path or config.MODEL_PATH
        self.session = get_session()
        self.user_item_matrix = None
        self.item_features_matrix = None
        self.feature_encoders = {}
        self.scaler = StandardScaler()
        
    def _build_user_item_matrix(self):
        """Build user-item interaction matrix from database."""
        interactions = self.session.query(UserInteraction).all()
        
        # Create interaction weights
        interaction_weights = {
            'view': 1.0,
            'like': 3.0,
            'cart': 4.0,
            'wishlist': 5.0,
            'purchase': 10.0
        }
        
        # Build matrix
        data = []
        for interaction in interactions:
            weight = interaction_weights.get(interaction.interaction_type, 1.0)
            if interaction.rating:
                weight *= interaction.rating / 5.0
            data.append({
                'user_id': interaction.user_id,
                'item_id': interaction.item_id,
                'weight': weight
            })
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        # Aggregate multiple interactions
        df = df.groupby(['user_id', 'item_id'])['weight'].sum().reset_index()
        
        # Create pivot table
        matrix = df.pivot_table(
            index='user_id',
            columns='item_id',
            values='weight',
            fill_value=0
        )
        
        return matrix
    
    def _build_item_features_matrix(self):
        """Build item feature matrix for content-based filtering."""
        items = self.session.query(FashionItem).all()
        
        features = []
        for item in items:
            features.append({
                'item_id': item.id,
                'category': item.category or 'unknown',
                'style': item.style or 'unknown',
                'color': item.color or 'unknown',
                'brand': item.brand or 'unknown',
                'price': item.price or 0,
                'season': item.season or 'all',
                'trending_score': item.trending_score or 0
            })
        
        if not features:
            return pd.DataFrame()
        
        df = pd.DataFrame(features)
        df.set_index('item_id', inplace=True)
        
        # Encode categorical features
        categorical_cols = ['category', 'style', 'color', 'brand', 'season']
        for col in categorical_cols:
            if col not in self.feature_encoders:
                self.feature_encoders[col] = LabelEncoder()
            df[f'{col}_encoded'] = self.feature_encoders[col].fit_transform(df[col])
        
        # Create price ranges
        if df['price'].max() > 0:
            df['price_range'] = pd.cut(df['price'], bins=5, labels=False)
        else:
            df['price_range'] = 0
        
        # Select numeric features
        feature_cols = [f'{col}_encoded' for col in categorical_cols] + ['price_range', 'trending_score']
        feature_matrix = df[feature_cols]
        
        # Normalize features
        feature_matrix = pd.DataFrame(
            self.scaler.fit_transform(feature_matrix),
            index=feature_matrix.index,
            columns=feature_matrix.columns
        )
        
        return feature_matrix
    
    def _collaborative_filtering(self, user_id: int, top_n: int = 10) -> List[Tuple[int, float]]:
        """
        Collaborative filtering: Find similar users and recommend items they liked.
        """
        if self.user_item_matrix is None or self.user_item_matrix.empty:
            return []
        
        if user_id not in self.user_item_matrix.index:
            return []
        
        # Calculate user similarity
        user_vector = self.user_item_matrix.loc[user_id].values.reshape(1, -1)
        similarities = cosine_similarity(user_vector, self.user_item_matrix.values)[0]
        
        # Get similar users (excluding self)
        similar_users = []
        for idx, sim in enumerate(similarities):
            other_user_id = self.user_item_matrix.index[idx]
            if other_user_id != user_id and sim > config.SIMILARITY_THRESHOLD:
                similar_users.append((other_user_id, sim))
        
        similar_users.sort(key=lambda x: x[1], reverse=True)
        similar_users = similar_users[:5]  # Top 5 similar users
        
        # Get items from similar users
        user_items = set(self.user_item_matrix.columns[self.user_item_matrix.loc[user_id] > 0])
        
        item_scores = {}
        for similar_user_id, similarity in similar_users:
            similar_user_items = self.user_item_matrix.loc[similar_user_id]
            for item_id, score in similar_user_items.items():
                if score > 0 and item_id not in user_items:
                    if item_id not in item_scores:
                        item_scores[item_id] = 0
                    item_scores[item_id] += score * similarity
        
        # Sort by score
        recommendations = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)
        return recommendations[:top_n]
    
    def _content_based_filtering(self, user_id: int, top_n: int = 10) -> List[Tuple[int, float]]:
        """
        Content-based filtering: Recommend items similar to user's preferences.
        """
        if self.item_features_matrix is None or self.item_features_matrix.empty:
            return []
        
        # Get user's interaction history
        user_interactions = self.session.query(UserInteraction).filter_by(user_id=user_id).all()
        
        if not user_interactions:
            return []
        
        # Build user profile from interacted items
        interacted_item_ids = [i.item_id for i in user_interactions if i.item_id in self.item_features_matrix.index]
        
        if not interacted_item_ids:
            return []
        
        # Calculate average feature vector for user's liked items
        user_profile = self.item_features_matrix.loc[interacted_item_ids].mean(axis=0).values.reshape(1, -1)
        
        # Calculate similarity with all items
        similarities = cosine_similarity(user_profile, self.item_features_matrix.values)[0]
        
        # Exclude already interacted items
        recommendations = []
        for idx, sim in enumerate(similarities):
            item_id = self.item_features_matrix.index[idx]
            if item_id not in interacted_item_ids:
                recommendations.append((item_id, sim))
        
        # Sort by similarity
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_n]
    
    def _get_trending_items(self, top_n: int = 10, days: int = 30) -> List[Tuple[int, float]]:
        """Get trending items based on recent interactions."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        recent_interactions = self.session.query(UserInteraction).filter(
            UserInteraction.timestamp >= cutoff_date
        ).all()
        
        item_counts = {}
        for interaction in recent_interactions:
            item_id = interaction.item_id
            if item_id not in item_counts:
                item_counts[item_id] = 0
            item_counts[item_id] += 1
        
        trending = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
        return trending[:top_n]
    
    def get_recommendations(self, user_id: int, top_n: int = None) -> List[Dict]:
        """
        Get personalized recommendations for a user using hybrid approach.
        
        Args:
            user_id: ID of the user
            top_n: Number of recommendations to return
            
        Returns:
            List of recommended fashion items with scores
        """
        if top_n is None:
            top_n = config.RECOMMENDATION_TOP_N
        
        # Build matrices
        self.user_item_matrix = self._build_user_item_matrix()
        self.item_features_matrix = self._build_item_features_matrix()
        
        # Get recommendations from different methods
        collab_recs = self._collaborative_filtering(user_id, top_n * 2)
        content_recs = self._content_based_filtering(user_id, top_n * 2)
        trending_recs = self._get_trending_items(top_n)
        
        # Combine recommendations with weighted scoring
        combined_scores = {}
        
        # Collaborative filtering (weight: 0.5)
        for item_id, score in collab_recs:
            combined_scores[item_id] = combined_scores.get(item_id, 0) + score * 0.5
        
        # Content-based filtering (weight: 0.4)
        for item_id, score in content_recs:
            combined_scores[item_id] = combined_scores.get(item_id, 0) + score * 0.4
        
        # Trending items (weight: 0.1)
        max_trend_score = max([s for _, s in trending_recs]) if trending_recs else 1
        for item_id, score in trending_recs:
            normalized_score = score / max_trend_score
            combined_scores[item_id] = combined_scores.get(item_id, 0) + normalized_score * 0.1
        
        # Sort by combined score
        final_recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        final_recommendations = final_recommendations[:top_n]
        
        # Fetch item details
        results = []
        for item_id, score in final_recommendations:
            item = self.session.query(FashionItem).filter_by(id=item_id).first()
            if item:
                results.append({
                    'item_id': item.id,
                    'name': item.name,
                    'category': item.category,
                    'brand': item.brand,
                    'price': item.price,
                    'style': item.style,
                    'color': item.color,
                    'image_url': item.image_url,
                    'recommendation_score': float(score),
                    'trending_score': item.trending_score
                })
        
        return results
    
    def update_user_preferences(self, user_id: int, interaction_data: Dict):
        """
        Update user preferences based on new interaction.
        This allows continuous learning from user behavior.
        """
        # Create new interaction
        interaction = UserInteraction(
            user_id=user_id,
            item_id=interaction_data['item_id'],
            interaction_type=interaction_data['interaction_type'],
            rating=interaction_data.get('rating'),
            timestamp=datetime.utcnow()
        )
        self.session.add(interaction)
        
        # Update or create preferences based on item features
        item = self.session.query(FashionItem).filter_by(id=interaction_data['item_id']).first()
        if item:
            preference_keys = ['category', 'style', 'color', 'brand']
            for key in preference_keys:
                value = getattr(item, key, None)
                if value:
                    pref = self.session.query(UserPreference).filter_by(
                        user_id=user_id,
                        preference_key=key,
                        preference_value=value
                    ).first()
                    
                    if pref:
                        # Increase weight for existing preference
                        pref.weight += 0.1
                        pref.updated_at = datetime.utcnow()
                    else:
                        # Create new preference
                        new_pref = UserPreference(
                            user_id=user_id,
                            preference_key=key,
                            preference_value=value,
                            weight=1.0
                        )
                        self.session.add(new_pref)
        
        self.session.commit()
    
    def save_model(self, filename: str = 'recommendation_model.pkl'):
        """Save the trained model to disk."""
        model_data = {
            'feature_encoders': self.feature_encoders,
            'scaler': self.scaler
        }
        
        os.makedirs(self.model_path, exist_ok=True)
        filepath = os.path.join(self.model_path, filename)
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filename: str = 'recommendation_model.pkl'):
        """Load a trained model from disk."""
        filepath = os.path.join(self.model_path, filename)
        if os.path.exists(filepath):
            model_data = joblib.load(filepath)
            self.feature_encoders = model_data['feature_encoders']
            self.scaler = model_data['scaler']
            print(f"Model loaded from {filepath}")
        else:
            print(f"Model file not found: {filepath}")
