"""
Flask API for Smart Fashion Trends application.
Provides endpoints for authentication, recommendations, and trend analysis.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import jwt
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data.models import User, FashionItem, init_db, get_session
from src.models.recommendation_engine import RecommendationEngine
from src.models.trend_analyzer import TrendAnalyzer
from config.config import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
CORS(app)

# Initialize database
init_db()

# Initialize models
recommendation_engine = RecommendationEngine()
trend_analyzer = TrendAnalyzer()


def token_required(f):
    """Decorator to require JWT token for protected routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated


@app.route('/')
def index():
    """API root endpoint."""
    return jsonify({
        'name': 'Smart Fashion Trends API',
        'version': '1.0.0',
        'endpoints': {
            'auth': {
                'register': 'POST /api/auth/register',
                'login': 'POST /api/auth/login'
            },
            'recommendations': {
                'get': 'GET /api/recommendations',
                'feedback': 'POST /api/recommendations/feedback'
            },
            'trends': {
                'all': 'GET /api/trends',
                'seasonal': 'GET /api/trends/seasonal/<season>'
            },
            'user': {
                'preferences': 'GET /api/user/preferences',
                'update_preferences': 'POST /api/user/preferences'
            }
        }
    })


# Authentication endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    session = get_session()
    
    # Check if user already exists
    existing_user = session.query(User).filter(
        (User.username == data['username']) | (User.email == data['email'])
    ).first()
    
    if existing_user:
        return jsonify({'error': 'User already exists'}), 409
    
    # Create new user
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    
    session.add(user)
    session.commit()
    
    # Generate token
    token = jwt.encode(
        {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=30)
        },
        config.JWT_SECRET_KEY,
        algorithm='HS256'
    )
    
    return jsonify({
        'message': 'User created successfully',
        'user_id': user.id,
        'username': user.username,
        'token': token
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user and return JWT token."""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    session = get_session()
    user = session.query(User).filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate token
    token = jwt.encode(
        {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=30)
        },
        config.JWT_SECRET_KEY,
        algorithm='HS256'
    )
    
    return jsonify({
        'message': 'Login successful',
        'user_id': user.id,
        'username': user.username,
        'token': token
    })


# Recommendation endpoints
@app.route('/api/recommendations', methods=['GET'])
@token_required
def get_recommendations(current_user_id):
    """Get personalized recommendations for the logged-in user."""
    top_n = request.args.get('top_n', default=10, type=int)
    
    try:
        recommendations = recommendation_engine.get_recommendations(current_user_id, top_n)
        
        return jsonify({
            'user_id': current_user_id,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommendations/feedback', methods=['POST'])
@token_required
def submit_feedback(current_user_id):
    """Submit feedback on a recommendation (like, purchase, etc.)."""
    data = request.get_json()
    
    if not data or not data.get('item_id') or not data.get('interaction_type'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        recommendation_engine.update_user_preferences(current_user_id, data)
        
        return jsonify({
            'message': 'Feedback recorded successfully',
            'user_id': current_user_id,
            'item_id': data['item_id'],
            'interaction_type': data['interaction_type']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Trend endpoints
@app.route('/api/trends', methods=['GET'])
def get_trends():
    """Get current fashion trends."""
    days = request.args.get('days', default=30, type=int)
    
    try:
        trends = trend_analyzer.analyze_trends(days)
        
        return jsonify({
            'trends': trends,
            'period_days': days,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trends/seasonal/<season>', methods=['GET'])
def get_seasonal_trends(season):
    """Get trends for a specific season."""
    valid_seasons = ['spring', 'summer', 'fall', 'winter']
    
    if season.lower() not in valid_seasons:
        return jsonify({'error': 'Invalid season. Must be one of: spring, summer, fall, winter'}), 400
    
    try:
        trends = trend_analyzer.get_seasonal_trends(season.lower())
        
        return jsonify({
            'season': season,
            'trends': trends,
            'count': len(trends),
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# User preference endpoints
@app.route('/api/user/preferences', methods=['GET'])
@token_required
def get_user_preferences(current_user_id):
    """Get user preferences."""
    session = get_session()
    user = session.query(User).filter_by(id=current_user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    preferences = []
    for pref in user.preferences:
        preferences.append({
            'key': pref.preference_key,
            'value': pref.preference_value,
            'weight': pref.weight,
            'updated_at': pref.updated_at.isoformat()
        })
    
    return jsonify({
        'user_id': current_user_id,
        'username': user.username,
        'preferences': preferences
    })


@app.route('/api/user/preferences', methods=['POST'])
@token_required
def update_user_preferences(current_user_id):
    """Update user preferences manually."""
    data = request.get_json()
    
    if not data or not isinstance(data, list):
        return jsonify({'error': 'Expected array of preferences'}), 400
    
    session = get_session()
    
    try:
        from ..data.models import UserPreference
        
        for pref_data in data:
            if not pref_data.get('key') or not pref_data.get('value'):
                continue
            
            # Check if preference exists
            existing = session.query(UserPreference).filter_by(
                user_id=current_user_id,
                preference_key=pref_data['key'],
                preference_value=pref_data['value']
            ).first()
            
            if existing:
                existing.weight = pref_data.get('weight', 1.0)
                existing.updated_at = datetime.utcnow()
            else:
                new_pref = UserPreference(
                    user_id=current_user_id,
                    preference_key=pref_data['key'],
                    preference_value=pref_data['value'],
                    weight=pref_data.get('weight', 1.0)
                )
                session.add(new_pref)
        
        session.commit()
        
        return jsonify({'message': 'Preferences updated successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })


if __name__ == '__main__':
    app.run(host=config.API_HOST, port=config.API_PORT, debug=config.DEBUG)
