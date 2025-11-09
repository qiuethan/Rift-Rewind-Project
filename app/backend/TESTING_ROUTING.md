# Testing Smart Routing System

This guide explains how to test the smart routing system that handles requests from the frontend.

## Overview

The smart routing system automatically determines what data to fetch based on the user's question and context. The frontend provides information via:
1. **Authentication header** - Contains JWT token with user ID
2. **Request body** - Contains prompt, optional match_id, champion_id, and page context

## Architecture

```
Frontend Request → API Endpoint → LLM Service → Smart Routing → Context Fetching → AI Response
```

### Flow:
1. Frontend sends request to `/api/llm/chat` with authentication
2. Backend extracts PUUID from user's JWT token
3. Smart routing analyzes the prompt to determine needed contexts
4. System fetches only the required data (summoner, champion progress, match)
5. AI generates response with appropriate context
6. Response returned to frontend

## API Endpoint

### POST `/api/llm/chat`

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "prompt": "How am I doing on Yasuo?",
  "match_id": "NA1_1234567890",  // Optional - for match-specific questions
  "champion_id": 157,             // Optional - for champion-specific questions
  "page_context": "champion_detail"  // Optional - for analytics
}
```

**Response:**
```json
{
  "text": "Based on your recent games with Yasuo...",
  "model_used": "claude-3-haiku",
  "complexity": "simple",
  "contexts_used": ["summoner", "champion_progress"],
  "metadata": {
    "page_context": "champion_detail",
    "champion_id": 157,
    "match_id": null
  }
}
```

## Testing Methods

### Method 1: Using the Test Script (Recommended)

Run the interactive test script that simulates frontend requests:

```bash
cd app/backend
python test_routing_with_headers.py
```

This script provides:
- **Dashboard Page Tests** - General questions without specific context
- **Champion Detail Page Tests** - Champion-specific questions
- **Match Detail Page Tests** - Match-specific questions
- **Custom Tests** - Your own test scenarios

### Method 2: Using the Original Test Script

Run the original smart routing tests:

```bash
cd app/backend
python test_smart_routing.py
```

This tests:
- Context classification
- Champion extraction
- Smart routing flow

### Method 3: Using HTTP Client (Postman, curl, etc.)

**Example with curl:**

```bash
# 1. Login to get JWT token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# 2. Use token to make chat request
curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -d '{
    "prompt": "How am I doing on Yasuo?",
    "champion_id": 157,
    "page_context": "champion_detail"
  }'
```

### Method 4: Using FastAPI Docs

1. Start the backend server:
   ```bash
   cd app/backend
   python main.py
   ```

2. Open browser to `http://localhost:8000/docs`

3. Authenticate:
   - Click "Authorize" button
   - Login via `/api/auth/login` to get token
   - Enter token in format: `Bearer <token>`

4. Test `/api/llm/chat` endpoint with different scenarios

## Test Scenarios

### Scenario 1: Dashboard - General Question
**Context:** User on dashboard, no specific champion or match selected

```json
{
  "prompt": "How am I doing overall?",
  "page_context": "dashboard"
}
```

**Expected Behavior:**
- Fetches: `summoner` context only
- Returns: General overview of player performance

### Scenario 2: Champion Detail - Champion-Specific Question
**Context:** User viewing Yasuo champion detail page

```json
{
  "prompt": "Am I improving on this champion?",
  "champion_id": 157,
  "page_context": "champion_detail"
}
```

**Expected Behavior:**
- Fetches: `summoner` + `champion_progress` contexts
- Returns: Analysis of Yasuo performance trends (EPS, CPS, win rate)

### Scenario 3: Match Detail - Match-Specific Question
**Context:** User viewing a specific match

```json
{
  "prompt": "What went wrong in this game?",
  "match_id": "NA1_1234567890",
  "page_context": "match_detail"
}
```

**Expected Behavior:**
- Fetches: `summoner` + `match` contexts
- Returns: Analysis of that specific match

### Scenario 4: Complex Question - Multiple Contexts
**Context:** User asks about champion performance in a specific match

```json
{
  "prompt": "How did I perform on Ahri in my last game?",
  "match_id": "NA1_1234567890",
  "champion_id": 103,
  "page_context": "match_detail"
}
```

**Expected Behavior:**
- Fetches: `summoner` + `champion_progress` + `match` contexts
- Returns: Comprehensive analysis combining champion stats and match performance

## Frontend Integration

### React/TypeScript Example

```typescript
// api/llm.ts
export async function chat(
  prompt: string,
  options?: {
    matchId?: string;
    championId?: number;
    pageContext?: string;
  }
) {
  const response = await fetch('/api/llm/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`, // Your auth token
    },
    body: JSON.stringify({
      prompt,
      match_id: options?.matchId,
      champion_id: options?.championId,
      page_context: options?.pageContext,
    }),
  });
  
  return response.json();
}

// Usage in components:

// Dashboard page
const response = await chat("How am I doing?", {
  pageContext: "dashboard"
});

// Champion detail page (Yasuo)
const response = await chat("Am I improving?", {
  championId: 157,
  pageContext: "champion_detail"
});

// Match detail page
const response = await chat("What went wrong?", {
  matchId: "NA1_1234567890",
  pageContext: "match_detail"
});
```

## Smart Routing Logic

The system uses AI to classify what contexts are needed:

1. **Context Classification** - Determines which data to fetch:
   - `summoner` - Basic player info (always included)
   - `champion_progress` - Champion-specific stats and trends
   - `match` - Specific match data

2. **Champion Extraction** - Identifies champion names in prompts:
   - "How am I doing on **Yasuo**?" → Fetches Yasuo stats
   - "Tips for **Lee Sin**" → Fetches Lee Sin stats

3. **Model Routing** - Selects appropriate AI model:
   - Simple questions → Claude Haiku (fast, cheap)
   - Complex analysis → Claude Sonnet (powerful, detailed)

## Metrics Explained

When champion progress context is included, the system provides:

### EPS (End-Game Performance Score)
- **Range:** 0-100 (always out of 100)
- **Measures:** How well the player performed in the match
- **Components:**
  - Combat (40%): KDA, damage dealt/taken
  - Economic (30%): Gold earned, CS, efficiency
  - Objective (30%): Turret damage, objective participation
- **Trend:** Positive = Skill improving, Negative = Skill declining

### CPS (Cumulative Power Score)
- **Range:** 0 to game_duration_in_minutes
- **Measures:** Champion's accumulated power during match
- **Components:**
  - Economic (45%): Gold and experience advantages
  - Offensive (35%): Damage output and kills
  - Defensive (20%): Survivability and mitigation
- **Trend:** Positive = Building correctly, Negative = Behind or incorrect build

## Troubleshooting

### "Bedrock not available"
- Check AWS credentials are configured
- Verify Bedrock service is enabled in your region

### "No summoner found"
- Ensure user has linked their League account via `/api/players/summoner`
- Check JWT token is valid

### "Champion not found"
- Verify champion_id is correct (use champion mapping)
- Check user has played games with that champion

### "Match not found"
- Verify match_id format (e.g., "NA1_1234567890")
- Ensure match exists in database
- Check user participated in that match

## Additional Endpoints

### POST `/api/llm/analyze-match`
Convenience endpoint for automatic match analysis without requiring a prompt.

**Request:**
```json
{
  "match_id": "NA1_1234567890"
}
```

### GET `/api/llm/health`
Check if LLM service is available.

**Response:**
```json
{
  "status": "healthy",
  "bedrock_available": true
}
```

## Performance Considerations

- **Caching:** Consider caching responses for identical prompts
- **Rate Limiting:** Implement rate limiting to prevent abuse
- **Async Processing:** Long analyses can be processed asynchronously
- **Context Size:** Larger contexts = higher costs, optimize what you fetch

## Next Steps

1. Test the routing with your own PUUID and data
2. Integrate the `/api/llm/chat` endpoint in your frontend
3. Add error handling and loading states
4. Implement streaming responses for better UX (future enhancement)
5. Add conversation history support (future enhancement)
