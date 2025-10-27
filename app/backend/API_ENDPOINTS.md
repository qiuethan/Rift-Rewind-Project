# Rift Rewind API - Complete Endpoint Reference

## 🔐 Authentication Endpoints

### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "player@example.com",
  "password": "SecurePass123",
  "summoner_name": "Faker",
  "region": "KR"
}

Response: 201 Created
{
  "user_id": "abc123",
  "email": "player@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "summoner_name": "Faker",
  "region": "KR"
}
```

### Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "player@example.com",
  "password": "SecurePass123"
}

Response: 200 OK
{
  "user_id": "abc123",
  "email": "player@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "summoner_name": "Faker",
  "region": "KR"
}
```

### Verify Token
```http
GET /api/auth/verify
Authorization: Bearer {token}

Response: 200 OK
{
  "user_id": "abc123",
  "email": "player@example.com",
  "valid": true
}
```

### Get Current User
```http
GET /api/auth/me
Authorization: Bearer {token}

Response: 200 OK
{
  "id": "abc123",
  "email": "player@example.com",
  "summoner_name": "Faker",
  "region": "KR",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## 👤 Player Endpoints

### Link Summoner Account
```http
POST /api/players/summoner
Authorization: Bearer {token}
Content-Type: application/json

{
  "summoner_name": "Faker",
  "region": "KR",
  "tag_line": "T1"
}

Response: 201 Created
{
  "id": "summoner_123",
  "summoner_name": "Faker",
  "region": "KR",
  "puuid": "abc-def-ghi",
  "summoner_level": 500,
  "profile_icon_id": 29,
  "last_updated": "2024-01-01T00:00:00Z"
}
```

### Get Linked Summoner
```http
GET /api/players/summoner
Authorization: Bearer {token}

Response: 200 OK
{
  "id": "summoner_123",
  "summoner_name": "Faker",
  "region": "KR",
  "puuid": "abc-def-ghi",
  "summoner_level": 500,
  "profile_icon_id": 29,
  "last_updated": "2024-01-01T00:00:00Z"
}
```

### Get Player Stats
```http
GET /api/players/stats/{summoner_id}

Response: 200 OK
{
  "summoner_id": "summoner_123",
  "total_games": 1000,
  "wins": 550,
  "losses": 450,
  "win_rate": 55.0,
  "favorite_champions": ["Ahri", "LeBlanc", "Syndra"],
  "average_kda": 4.2,
  "average_cs_per_min": 8.5
}
```

### Get Match History
```http
GET /api/players/matches?count=20
Authorization: Bearer {token}

Response: 200 OK
[
  "KR_123456789",
  "KR_123456788",
  "KR_123456787",
  ...
]
```

---

## 🎮 Match Endpoints

### Get Match Timeline
```http
GET /api/matches/{match_id}/timeline?region=americas

Response: 200 OK
{
  "match_id": "NA1_123456789",
  "frames": [
    {
      "timestamp": 60000,
      "participantFrames": {
        "1": {
          "participant_id": 1,
          "level": 3,
          "current_gold": 500,
          "total_gold": 1200,
          "xp": 800,
          "minions_killed": 15,
          "champion_stats": {...},
          "damage_stats": {...},
          "position": {"x": 1000, "y": 2000}
        },
        ...
      },
      "events": [...]
    },
    ...
  ],
  "frame_interval": 60000
}
```

### Get Match Summary
```http
GET /api/matches/{match_id}/summary?region=americas

Response: 200 OK
{
  "match_id": "NA1_123456789",
  "game_duration": 1800,
  "game_mode": "CLASSIC",
  "game_type": "MATCHED_GAME",
  "participants": [...],
  "teams": [...]
}
```

### Get Participant Data
```http
GET /api/matches/{match_id}/participant/{participant_id}

Response: 200 OK
{
  "participant_id": 1,
  "champion_name": "Ahri",
  "kills": 10,
  "deaths": 2,
  "assists": 15,
  "cs": 250,
  "gold": 15000
}
```

---

## 🏆 Champion Endpoints

### Get All Champions
```http
GET /api/champions/

Response: 200 OK
[
  {
    "id": "ahri",
    "name": "Ahri",
    "title": "the Nine-Tailed Fox",
    "tags": ["Mage", "Assassin"],
    "stats": {...},
    "abilities": [...]
  },
  ...
]
```

### Get Champion by ID
```http
GET /api/champions/{champion_id}

Response: 200 OK
{
  "id": "ahri",
  "name": "Ahri",
  "title": "the Nine-Tailed Fox",
  "tags": ["Mage", "Assassin"],
  "stats": {
    "hp": 526,
    "attack": 53,
    "armor": 21,
    "magic_resist": 30
  },
  "abilities": [
    {
      "name": "Orb of Deception",
      "type": "Q",
      "description": "Ahri sends out and pulls back her orb...",
      "cooldown": [7, 6.5, 6, 5.5, 5],
      "cost": [65, 70, 75, 80, 85]
    },
    ...
  ]
}
```

### Get Champion Recommendations
```http
POST /api/champions/recommendations
Authorization: Bearer {token}
Content-Type: application/json

{
  "summoner_id": "summoner_123",
  "limit": 5,
  "include_reasoning": true
}

Response: 200 OK
{
  "summoner_id": "summoner_123",
  "recommendations": [
    {
      "champion_id": "syndra",
      "champion_name": "Syndra",
      "similarity_score": 0.85,
      "reasoning": "Similar burst mage playstyle with skill-shot abilities",
      "similar_abilities": ["Q - Orb mechanics", "E - CC ability"],
      "playstyle_match": "Control Mage"
    },
    {
      "champion_id": "leblanc",
      "champion_name": "LeBlanc",
      "similarity_score": 0.80,
      "reasoning": "High mobility assassin mage with outplay potential",
      "similar_abilities": ["W - Dash ability", "R - Ultimate flexibility"],
      "playstyle_match": "Assassin Mage"
    },
    ...
  ],
  "based_on_champions": ["Ahri", "Lux", "Orianna"]
}
```

### Calculate Champion Similarity
```http
POST /api/champions/similarity
Content-Type: application/json

{
  "champion_a": "ahri",
  "champion_b": "syndra",
  "include_details": true
}

Response: 200 OK
{
  "champion_a": "ahri",
  "champion_b": "syndra",
  "similarity_score": 0.85,
  "ability_similarity": 0.80,
  "stat_similarity": 0.75,
  "playstyle_similarity": 0.90
}
```

---

## 📊 Analytics Endpoints

### Analyze Performance
```http
POST /api/analytics/performance
Authorization: Bearer {token}
Content-Type: application/json

{
  "match_id": "NA1_123456789",
  "summoner_id": "summoner_123",
  "include_timeline": true
}

Response: 200 OK
{
  "match_id": "NA1_123456789",
  "summoner_id": "summoner_123",
  "overall_grade": "A",
  "metrics": {
    "match_id": "NA1_123456789",
    "participant_id": 1,
    "kda": 4.5,
    "cs_per_min": 8.2,
    "gold_per_min": 450,
    "damage_per_min": 650,
    "vision_score": 45,
    "kill_participation": 75.0
  },
  "phase_analysis": [
    {
      "phase": "early",
      "cs_advantage": 10.0,
      "gold_advantage": 300.0,
      "xp_advantage": 150.0,
      "deaths": 0,
      "kills": 2,
      "assists": 1
    },
    {
      "phase": "mid",
      "cs_advantage": -5.0,
      "gold_advantage": 100.0,
      "xp_advantage": 50.0,
      "deaths": 1,
      "kills": 3,
      "assists": 5
    },
    {
      "phase": "late",
      "cs_advantage": 5.0,
      "gold_advantage": 500.0,
      "xp_advantage": 200.0,
      "deaths": 1,
      "kills": 5,
      "assists": 9
    }
  ],
  "strengths": [
    "Excellent KDA - Great at staying alive and contributing to kills",
    "Strong farming - Consistently high CS per minute",
    "High kill participation - Active in team fights",
    "Good vision control - Strong map awareness"
  ],
  "weaknesses": [
    "Mid-game CS dip - Lost some farm during rotations"
  ],
  "recommendations": [
    "Continue current gameplay and focus on consistency",
    "Practice maintaining CS during mid-game rotations"
  ]
}
```

### Get Skill Progression
```http
POST /api/analytics/progression
Authorization: Bearer {token}
Content-Type: application/json

{
  "summoner_id": "summoner_123",
  "champion_id": "ahri",
  "time_range_days": 30
}

Response: 200 OK
{
  "summoner_id": "summoner_123",
  "champion_id": "ahri",
  "time_range_days": 30,
  "games_analyzed": 50,
  "improvement_metrics": {
    "kda": 0.8,
    "cs_per_min": 1.2,
    "vision_score": 10.0,
    "kill_participation": 5.0
  },
  "skill_trends": {
    "kda": [3.0, 3.2, 3.5, 3.7, 3.8],
    "cs_per_min": [7.0, 7.3, 7.6, 7.9, 8.2],
    "vision_score": [25, 28, 32, 35, 35],
    "kill_participation": [60, 62, 65, 68, 65]
  },
  "current_rank": "Platinum II"
}
```

### Generate AI Insights
```http
POST /api/analytics/insights
Authorization: Bearer {token}
Content-Type: application/json

{
  "summoner_id": "summoner_123",
  "match_ids": [
    "NA1_123456789",
    "NA1_123456788",
    "NA1_123456787"
  ],
  "focus_areas": ["farming", "teamfighting"]
}

Response: 200 OK
{
  "summoner_id": "summoner_123",
  "insights": [
    "Your CS/min has improved by 15% over the last 10 games",
    "You tend to die more in mid-game teamfights - work on positioning",
    "Your vision score is above average for your rank",
    "Strong early game performance across all matches",
    "Consider playing more control mages to expand your champion pool"
  ],
  "key_patterns": [
    "Strong early game laning phase",
    "Consistent farming patterns",
    "High kill participation in winning games",
    "Lower vision score in losing games"
  ],
  "actionable_tips": [
    "Focus on warding river before objectives spawn",
    "Practice team fight positioning in practice tool",
    "Maintain CS focus during mid-game rotations",
    "Place control wards in enemy jungle before objectives"
  ],
  "champion_pool_suggestions": [
    "Syndra - Similar playstyle, strong team fight control",
    "Orianna - Control mage, teaches positioning",
    "Viktor - Scaling mage, similar to your playstyle"
  ]
}
```

---

## ❤️ Health Endpoints

### Health Check
```http
GET /api/health/

Response: 200 OK
{
  "status": "healthy",
  "app_name": "Rift Rewind API",
  "version": "1.0.0"
}
```

### Ping
```http
GET /api/health/ping

Response: 200 OK
{
  "message": "pong"
}
```

---

## 🔒 Authentication

Most endpoints require authentication. Include the JWT token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Protected Endpoints
- All `/api/auth/*` except register/login
- All `/api/players/*` except stats
- All `/api/analytics/*`
- `/api/champions/recommendations`

### Public Endpoints
- `/api/health/*`
- `/api/champions/*` (except recommendations)
- `/api/matches/*`
- `/api/players/stats/{summoner_id}`

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "error": true,
  "message": "Validation error",
  "status_code": 400
}
```

### 401 Unauthorized
```json
{
  "error": true,
  "message": "Invalid authentication token",
  "status_code": 401
}
```

### 404 Not Found
```json
{
  "error": true,
  "message": "Resource not found",
  "status_code": 404
}
```

### 422 Validation Error
```json
{
  "error": true,
  "message": "Validation error",
  "details": [
    {
      "field": "body.email",
      "message": "value is not a valid email address",
      "type": "value_error.email"
    }
  ],
  "status_code": 422
}
```

### 500 Internal Server Error
```json
{
  "error": true,
  "message": "Internal server error",
  "status_code": 500
}
```

---

## 📝 Rate Limiting

Currently not implemented. For production, consider:
- 100 requests per minute per IP
- 1000 requests per hour per user
- Special limits for analytics endpoints

---

## 🧪 Testing with cURL

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456"}'

# Get champions (public)
curl http://localhost:8000/api/champions/

# Get player stats (protected)
curl http://localhost:8000/api/players/summoner \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📚 Interactive Documentation

Visit these URLs when the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both provide interactive API testing!
