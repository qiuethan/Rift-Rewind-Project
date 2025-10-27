# Riot API Setup Guide

Official Riot Games API Documentation: **https://developer.riotgames.com/apis**

## 🔑 Getting Your API Key

1. Go to [Riot Developer Portal](https://developer.riotgames.com/)
2. Sign in with your Riot Games account
3. Navigate to your **Dashboard**
4. Copy your **Development API Key**

⚠️ **Important:** Development keys expire every 24 hours. For production, apply for a production key.

## 🌍 Regional Routing

Riot API uses regional routing. Configure the correct region for your users.

### Regional Endpoints

| Region | Endpoint | Covers |
|--------|----------|--------|
| **Americas** | `americas.api.riotgames.com` | NA, BR, LAN, LAS |
| **Europe** | `europe.api.riotgames.com` | EUW, EUNE, TR, RU |
| **Asia** | `asia.api.riotgames.com` | KR, JP |
| **SEA** | `sea.api.riotgames.com` | OCE, PH, SG, TH, TW, VN |

### Platform Routes (for specific endpoints)

- `na1.api.riotgames.com` - North America
- `br1.api.riotgames.com` - Brazil
- `euw1.api.riotgames.com` - Europe West
- `eun1.api.riotgames.com` - Europe Nordic & East
- `kr.api.riotgames.com` - Korea
- `jp1.api.riotgames.com` - Japan
- `la1.api.riotgames.com` - Latin America North
- `la2.api.riotgames.com` - Latin America South
- `oc1.api.riotgames.com` - Oceania
- `tr1.api.riotgames.com` - Turkey
- `ru.api.riotgames.com` - Russia

## 🔧 Configuration

Edit your `backend/.env`:

```env
# Riot API (Get your key from https://developer.riotgames.com/apis)
RIOT_API_KEY=RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
RIOT_API_BASE_URL=https://americas.api.riotgames.com
```

**Change region if needed:**
```env
# For Europe
RIOT_API_BASE_URL=https://europe.api.riotgames.com

# For Asia
RIOT_API_BASE_URL=https://asia.api.riotgames.com

# For SEA
RIOT_API_BASE_URL=https://sea.api.riotgames.com
```

## 📊 Key API Endpoints

### 1. Summoner API (v4)
Get summoner information by name, PUUID, or account ID.

```
GET /lol/summoner/v4/summoners/by-name/{summonerName}
GET /lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}
GET /lol/summoner/v4/summoners/by-account/{encryptedAccountId}
GET /lol/summoner/v4/summoners/{encryptedSummonerId}
```

**Example:**
```bash
curl -X GET "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/Hide%20on%20bush" \
  -H "X-Riot-Token: RGAPI-your-key-here"
```

### 2. Match API (v5)
Get match history and detailed match data.

```
GET /lol/match/v5/matches/by-puuid/{puuid}/ids
GET /lol/match/v5/matches/{matchId}
GET /lol/match/v5/matches/{matchId}/timeline
```

**Example:**
```bash
# Get match IDs
curl -X GET "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20" \
  -H "X-Riot-Token: RGAPI-your-key-here"

# Get match details
curl -X GET "https://americas.api.riotgames.com/lol/match/v5/matches/NA1_1234567890" \
  -H "X-Riot-Token: RGAPI-your-key-here"
```

### 3. Champion Mastery API (v4)
Get champion mastery scores and levels.

```
GET /lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}
GET /lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}/by-champion/{championId}
GET /lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}/top
GET /lol/champion-mastery/v4/scores/by-puuid/{encryptedPUUID}
```

### 4. League API (v4)
Get ranked information and league entries.

```
GET /lol/league/v4/entries/by-summoner/{encryptedSummonerId}
GET /lol/league/v4/entries/{queue}/{tier}/{division}
GET /lol/league/v4/challengerleagues/by-queue/{queue}
GET /lol/league/v4/grandmasterleagues/by-queue/{queue}
GET /lol/league/v4/masterleagues/by-queue/{queue}
```

### 5. Champion API (v3)
Get champion rotation and static data.

```
GET /lol/platform/v3/champion-rotations
```

### 6. Spectator API (v5)
Get current game information for active games.

```
GET /lol/spectator/v5/active-games/by-summoner/{encryptedPUUID}
GET /lol/spectator/v5/featured-games
```

## 📝 Rate Limits

### Development Key
- **20 requests per second**
- **100 requests per 2 minutes**

### Production Key (Personal)
- **50 requests per second**
- **300 requests per 2 minutes**

### Production Key (Application)
- Custom rate limits based on your application needs
- Apply through the Riot Developer Portal

## 🔒 Best Practices

### 1. Always Include API Key in Header
```python
headers = {
    "X-Riot-Token": settings.RIOT_API_KEY
}
```

### 2. Handle Rate Limits
```python
if response.status_code == 429:
    retry_after = response.headers.get('Retry-After')
    # Wait and retry
```

### 3. Cache Responses
```python
# Cache summoner data (changes rarely)
# Cache match data (never changes)
# Don't cache active game data (changes frequently)
```

### 4. Use Regional Routing Correctly
- Use **regional endpoints** for match data (v5)
- Use **platform endpoints** for summoner data (v4)

### 5. Handle Errors Gracefully
```python
# 400 - Bad request
# 401 - Unauthorized (invalid API key)
# 403 - Forbidden (API key expired or blacklisted)
# 404 - Data not found
# 429 - Rate limit exceeded
# 500 - Internal server error
# 503 - Service unavailable
```

## 🧪 Testing Your Setup

### Test API Key
```bash
curl -X GET "https://na1.api.riotgames.com/lol/platform/v3/champion-rotations" \
  -H "X-Riot-Token: RGAPI-your-key-here"
```

### Test Summoner Lookup
```bash
curl -X GET "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/Doublelift" \
  -H "X-Riot-Token: RGAPI-your-key-here"
```

### Test Match History
```bash
# First get PUUID from summoner lookup, then:
curl -X GET "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=5" \
  -H "X-Riot-Token: RGAPI-your-key-here"
```

## 🚀 Production Deployment

### Apply for Production Key

1. Go to [Riot Developer Portal](https://developer.riotgames.com/)
2. Navigate to **Apps**
3. Click **Register Product**
4. Fill out the application:
   - Product name
   - Description
   - Expected traffic
   - Use case
5. Wait for approval (usually 1-2 weeks)

### Production Checklist
- [ ] Production API key obtained
- [ ] Rate limiting implemented
- [ ] Response caching configured
- [ ] Error handling in place
- [ ] Monitoring and logging set up
- [ ] Regional routing configured correctly

## 📚 Resources

- **Official API Docs**: https://developer.riotgames.com/apis
- **API Status**: https://developer.riotgames.com/api-status/
- **Community Discord**: https://discord.gg/riotgamesdevrel
- **API Policies**: https://developer.riotgames.com/policies

## 🐛 Common Issues

### "401 Unauthorized"
- API key is invalid or expired
- Regenerate your development key daily
- Check that key is in `X-Riot-Token` header

### "403 Forbidden"
- API key is blacklisted
- You violated rate limits too many times
- Contact Riot support

### "404 Not Found"
- Summoner name doesn't exist
- Match ID is invalid
- Wrong regional endpoint

### "429 Rate Limit Exceeded"
- Too many requests
- Implement exponential backoff
- Check `Retry-After` header

### "Data Mismatch"
- Using wrong regional endpoint
- Match data requires regional routing (americas, europe, asia, sea)
- Summoner data requires platform routing (na1, euw1, etc.)

## ✅ Quick Start Checklist

- [ ] Riot account created
- [ ] Development API key obtained from https://developer.riotgames.com/apis
- [ ] API key added to `backend/.env`
- [ ] Correct region configured
- [ ] Test API call successful
- [ ] Rate limiting understood

Your Riot API integration is ready! 🎮
