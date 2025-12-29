# Smart Fashion Trends - AI Recommendation System

An AI-powered fashion trending and recommendation system that provides personalized fashion recommendations based on user preferences and current trends.

## Features

- **Personalized Recommendations**: AI model trained on user-specific data
- **Trend Analysis**: Real-time fashion trend detection and analysis
- **User Authentication**: Secure user login and data management
- **Privacy-Focused**: Compliant with data privacy policies
- **Collaborative Filtering**: Recommendations based on similar users
- **Content-Based Filtering**: Recommendations based on item features

## Installation

1. Clone the repository:
```bash
git clone https://github.com/PradeepMedikonda/smartFashionTrends.git
cd smartFashionTrends
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

### Starting the API Server

```bash
python src/api/app.py
```

The API will be available at `http://localhost:5000`

### Training the Model

```bash
python src/train_model.py
```

### Getting Recommendations

```python
from src.models.recommendation_engine import RecommendationEngine

engine = RecommendationEngine()
recommendations = engine.get_recommendations(user_id=1, top_n=10)
```

## API Endpoints

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user
- `GET /api/recommendations/{user_id}` - Get personalized recommendations
- `GET /api/trends` - Get current fashion trends
- `POST /api/user/preferences` - Update user preferences
- `POST /api/user/feedback` - Submit feedback on recommendations

## Project Structure

```
smartFashionTrends/
├── src/
│   ├── models/          # AI models and algorithms
│   ├── api/             # Flask API endpoints
│   ├── data/            # Data models and database
│   └── utils/           # Utility functions
├── config/              # Configuration files
├── data/                # Training data
├── tests/               # Unit tests
├── policies/            # Privacy and usage policies
└── requirements.txt     # Python dependencies
```

## Privacy & Data Policy

All user data is handled according to our [Privacy Policy](policies/PRIVACY_POLICY.md). Key points:

- User data is only used for personalized recommendations
- No data is shared with third parties
- Users can request data deletion at any time
- All data is encrypted at rest and in transit

## Technologies Used

- **Python 3.8+**
- **TensorFlow/Keras** - Deep learning models
- **Scikit-learn** - Machine learning algorithms
- **Flask** - REST API
- **SQLAlchemy** - Database ORM
- **NumPy/Pandas** - Data processing

## License

MIT License

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.