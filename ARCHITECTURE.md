# System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Smart Fashion Trends System                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                           User Interface                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Registration │  │    Login     │  │ Preferences  │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         REST API Layer                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Flask API (src/api/app.py)                                    │  │
│  │                                                                │  │
│  │  /api/auth/register  →  User Registration                     │  │
│  │  /api/auth/login     →  JWT Authentication                    │  │
│  │  /api/recommendations → Get Personalized Recommendations      │  │
│  │  /api/trends         →  Get Fashion Trends                    │  │
│  │  /api/user/preferences → Manage User Preferences              │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Recommendation Engine (src/models/recommendation_engine.py)  │   │
│  │                                                               │   │
│  │  ┌────────────────────┐  ┌──────────────────┐              │   │
│  │  │ Collaborative      │  │  Content-Based   │              │   │
│  │  │ Filtering (50%)    │  │  Filtering (40%) │              │   │
│  │  │                    │  │                  │              │   │
│  │  │ - Find similar     │  │ - Match item     │              │   │
│  │  │   users            │  │   features       │              │   │
│  │  │ - Recommend items  │  │ - User profile   │              │   │
│  │  │   they liked       │  │   matching       │              │   │
│  │  └────────────────────┘  └──────────────────┘              │   │
│  │                                                               │   │
│  │  ┌──────────────────┐                                        │   │
│  │  │  Trending (10%)  │                                        │   │
│  │  │                  │                                        │   │
│  │  │ - Popular items  │                                        │   │
│  │  │ - Recency boost  │                                        │   │
│  │  └──────────────────┘                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Trend Analyzer (src/models/trend_analyzer.py)               │   │
│  │                                                               │   │
│  │  - Multi-dimensional trend analysis                          │   │
│  │  - Temporal pattern detection                                │   │
│  │  - Growth rate calculation                                   │   │
│  │  - Seasonal trends                                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Data Access Layer                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ SQLAlchemy ORM (src/data/models.py)                          │  │
│  │                                                                │  │
│  │  ┌──────────┐  ┌──────────────┐  ┌────────────────┐         │  │
│  │  │   User   │  │ FashionItem  │  │ UserInteraction│         │  │
│  │  └──────────┘  └──────────────┘  └────────────────┘         │  │
│  │                                                                │  │
│  │  ┌────────────────┐                                           │  │
│  │  │ UserPreference │                                           │  │
│  │  └────────────────┘                                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          Database Layer                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ SQLite / PostgreSQL / MySQL                                   │  │
│  │                                                                │  │
│  │  Tables: users, fashion_items, user_interactions,             │  │
│  │          user_preferences                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      Supporting Components                           │
│                                                                       │
│  ┌───────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │Configuration  │  │  Utilities   │  │  Privacy & Policies    │  │
│  │(config/)      │  │  (src/utils/)│  │  (policies/)           │  │
│  │               │  │              │  │                        │  │
│  │- Environment  │  │- Data gen    │  │- PRIVACY_POLICY.md     │  │
│  │- Model params │  │- Sample data │  │- DATA_USAGE.md         │  │
│  └───────────────┘  └──────────────┘  └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘


Data Flow for Recommendation Request:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. User → API Request (GET /api/recommendations)
2. API → JWT Validation
3. API → RecommendationEngine.get_recommendations(user_id)
4. Engine → Build user-item matrix from database
5. Engine → Build item features matrix
6. Engine → Apply collaborative filtering
7. Engine → Apply content-based filtering
8. Engine → Add trending boost
9. Engine → Combine weighted scores
10. Engine → Query item details from database
11. API → Return JSON response with recommendations


User Interaction Feedback Flow:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. User → API Request (POST /api/recommendations/feedback)
2. API → Create UserInteraction record
3. API → Extract item features
4. API → Update/Create UserPreference records
5. System → Continuously learns and adapts
6. Next recommendation → Reflects updated preferences


Trend Analysis Flow:
━━━━━━━━━━━━━━━━━━━━

1. TrendAnalyzer → Query recent interactions (30 days)
2. Analyzer → Apply interaction weights
3. Analyzer → Apply recency decay
4. Analyzer → Aggregate by dimensions (category, style, color, brand)
5. Analyzer → Calculate growth rates (week-over-week)
6. Analyzer → Update trending scores in database
7. RecommendationEngine → Use trending scores in recommendations
```
