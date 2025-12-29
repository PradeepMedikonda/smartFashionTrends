# Quick Start Guide

This guide will help you get started with the Smart Fashion Trends AI recommendation system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env if needed (optional for local development)
```

### 3. Initialize and Train the Model

```bash
# This will:
# - Create the database
# - Generate sample data (users, items, interactions)
# - Train the recommendation model
# - Calculate trending scores

python src/train_model.py
```

Expected output:
```
Initializing sample data...
Generated 100 sample fashion items
Generated 20 sample users
Generated 500 sample interactions
Sample data initialization complete!
Model training complete!
```

### 4. Test the System

Run the example usage script:

```bash
python examples/example_usage.py
```

This will demonstrate:
- Getting personalized recommendations
- Analyzing fashion trends
- Simulating user interactions
- Updating recommendations based on feedback

### 5. Run Tests

```bash
# Test recommendation engine
python tests/test_recommendations.py

# Test trend analyzer
python tests/test_trends.py

# Test API endpoints
python tests/test_api.py
```

### 6. Start the API Server

```bash
python src/api/app.py
```

The API will be available at: `http://localhost:5000`

## Using the API

### Register a New User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "fashionista",
    "email": "fashionista@example.com",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "message": "User created successfully",
  "user_id": 1,
  "username": "fashionista",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "fashionista",
    "password": "securepassword123"
  }'
```

### Get Recommendations

```bash
curl -X GET http://localhost:5000/api/recommendations \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Submit Feedback

```bash
curl -X POST http://localhost:5000/api/recommendations/feedback \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": 5,
    "interaction_type": "like",
    "rating": 5.0
  }'
```

### Get Fashion Trends

```bash
curl -X GET http://localhost:5000/api/trends
```

### Get Seasonal Trends

```bash
curl -X GET http://localhost:5000/api/trends/seasonal/summer
```

## Understanding the System

### How Recommendations Work

The system uses a **hybrid approach**:

1. **Collaborative Filtering** (50% weight)
   - Finds users with similar tastes
   - Recommends items liked by similar users
   
2. **Content-Based Filtering** (40% weight)
   - Analyzes item features (category, style, color, brand)
   - Recommends items similar to user's preferences
   
3. **Trending Items** (10% weight)
   - Incorporates popular items
   - Ensures fresh, relevant recommendations

### User-Specific Training

- Each user's interaction history trains their personal model
- Preferences are continuously updated based on feedback
- The more a user interacts, the better the recommendations

### Privacy Features

- User data is isolated and encrypted
- Personal models don't share data between users
- Trend analysis uses anonymized aggregate data
- See `policies/PRIVACY_POLICY.md` for details

## Customization

### Adjust Recommendation Weights

Edit `config/config.py`:

```python
FEATURE_WEIGHTS = {
    'category': 0.3,
    'style': 0.25,
    'color': 0.15,
    'brand': 0.15,
    'price_range': 0.1,
    'season': 0.05
}
```

### Change Model Parameters

Edit `config/config.py`:

```python
RECOMMENDATION_TOP_N = 10
MIN_INTERACTIONS = 5
SIMILARITY_THRESHOLD = 0.5
```

## Troubleshooting

### "No module named 'src'"

Make sure you're in the project root directory and have activated the virtual environment.

### "No data found"

Run the training script: `python src/train_model.py`

### Port 5000 already in use

Change the port in `.env`:
```
API_PORT=8000
```

## Next Steps

- Integrate with a frontend application
- Connect to a real product database
- Deploy to production server
- Add more features (image analysis, outfit recommendations)
- Implement A/B testing for algorithm improvements

## Support

For questions or issues:
- Check documentation in `README.md`
- Review privacy policies in `policies/`
- Run tests to verify installation

Enjoy using Smart Fashion Trends! 🎨👗👔
