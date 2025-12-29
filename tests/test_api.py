"""
Test suite for API endpoints.
"""
import unittest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.app import app
from src.data.models import init_db
from src.utils.data_generator import initialize_sample_data


class TestAPI(unittest.TestCase):
    """Test cases for API endpoints."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database and sample data."""
        # Use in-memory SQLite for testing
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        init_db()
        initialize_sample_data()
    
    def setUp(self):
        """Set up test client."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.token = None
    
    def test_index(self):
        """Test API root endpoint."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('name', data)
        print("✓ API root endpoint working")
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        print("✓ Health check endpoint working")
    
    def test_register_user(self):
        """Test user registration."""
        response = self.client.post('/api/auth/register', 
            json={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpassword123'
            })
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertIn('user_id', data)
        self.token = data['token']
        print("✓ User registration working")
    
    def test_login_user(self):
        """Test user login."""
        # First register
        self.client.post('/api/auth/register', 
            json={
                'username': 'logintest',
                'email': 'login@example.com',
                'password': 'password123'
            })
        
        # Then login
        response = self.client.post('/api/auth/login',
            json={
                'username': 'logintest',
                'password': 'password123'
            })
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.token = data['token']
        print("✓ User login working")
    
    def test_get_trends(self):
        """Test getting trends."""
        response = self.client.get('/api/trends')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('trends', data)
        print("✓ Trends endpoint working")
    
    def test_get_recommendations_without_auth(self):
        """Test recommendations endpoint requires authentication."""
        response = self.client.get('/api/recommendations')
        self.assertEqual(response.status_code, 401)
        print("✓ Authentication required for recommendations")
    
    def test_get_recommendations_with_auth(self):
        """Test getting recommendations with authentication."""
        # Login first
        self.client.post('/api/auth/register', 
            json={
                'username': 'rectest',
                'email': 'rec@example.com',
                'password': 'password123'
            })
        
        login_response = self.client.post('/api/auth/login',
            json={
                'username': 'rectest',
                'password': 'password123'
            })
        
        token = json.loads(login_response.data)['token']
        
        # Get recommendations
        response = self.client.get('/api/recommendations',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('recommendations', data)
        print("✓ Recommendations endpoint working")


if __name__ == '__main__':
    print("\nRunning API Tests...")
    print("=" * 60)
    unittest.main(verbosity=2)
