# Supabase Setup Guide for Rift Rewind

## 🚀 Quick Setup

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up / Log in
3. Click "New Project"
4. Fill in:
   - **Project name**: rift-rewind
   - **Database password**: (save this!)
   - **Region**: Choose closest to you
5. Wait for project to be created (~2 minutes)

### 2. Get Your Credentials

Once your project is ready:

1. Go to **Settings** → **API**
2. Copy these values to your `.env` file:
   - **Project URL** → `SUPABASE_URL`
   - **API Key** → `SUPABASE_KEY`

#### 🔑 API Keys

Supabase provides different keys for different purposes:
- **anon** / **publishable** key - For frontend/client-side (limited permissions)
- **service_role** key - For backend/server-side (elevated permissions)

**For this backend, use the `service_role` key.**

**For this backend, use the `service_role` key:**

⚠️ **Important**: The backend needs elevated permissions to bypass Row Level Security (RLS) and perform admin operations. Use the `service_role` key (NOT the anon/publishable key).

**Note**: The new `sb_secret_...` keys are not yet fully supported by supabase-py v2.3.0. Use the legacy `service_role` key.

To get your `service_role` key:
1. Go to **Settings** → **API**
2. Scroll down to find the **service_role** key
3. Click the copy button (it's a long JWT token starting with `eyJ...`)

Example `.env`:
```bash
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjM4MzY3MjAwLCJleHAiOjE5NTM5NDMyMDB9...
```

🔒 **Security Note**: Never commit this key or expose it in client-side code!

📖 **Learn more**: [Supabase API Keys Update](https://github.com/orgs/supabase/discussions/29260)

### 3. Create Database Tables

Run these SQL commands in the Supabase SQL Editor:

#### Users Table
```sql
-- Users table (extends Supabase Auth)
CREATE TABLE users (
  id UUID REFERENCES auth.users PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  summoner_name TEXT,
  region TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
CREATE POLICY "Users can read own data"
  ON users FOR SELECT
  USING (auth.uid() = id);

-- Users can update their own data
CREATE POLICY "Users can update own data"
  ON users FOR UPDATE
  USING (auth.uid() = id);
```

#### Summoners Table
```sql
-- Summoners table (linked LoL accounts)
CREATE TABLE summoners (
  id TEXT PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  summoner_name TEXT NOT NULL,
  region TEXT NOT NULL,
  puuid TEXT NOT NULL,
  summoner_level INTEGER,
  profile_icon_id INTEGER,
  last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE summoners ENABLE ROW LEVEL SECURITY;

-- Users can read their own summoners
CREATE POLICY "Users can read own summoners"
  ON summoners FOR SELECT
  USING (auth.uid() = user_id);

-- Users can insert their own summoners
CREATE POLICY "Users can insert own summoners"
  ON summoners FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can update their own summoners
CREATE POLICY "Users can update own summoners"
  ON summoners FOR UPDATE
  USING (auth.uid() = user_id);
```

#### Match Timelines Table
```sql
-- Match timelines table (cached match data)
CREATE TABLE match_timelines (
  match_id TEXT PRIMARY KEY,
  frames JSONB NOT NULL,
  frame_interval INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS (public read for cached data)
ALTER TABLE match_timelines ENABLE ROW LEVEL SECURITY;

-- Anyone can read match timelines
CREATE POLICY "Anyone can read match timelines"
  ON match_timelines FOR SELECT
  TO authenticated
  USING (true);
```

#### Champions Table
```sql
-- Champions table (champion data)
CREATE TABLE champions (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  title TEXT,
  tags TEXT[],
  stats JSONB,
  abilities JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS (public read)
ALTER TABLE champions ENABLE ROW LEVEL SECURITY;

-- Anyone can read champions
CREATE POLICY "Anyone can read champions"
  ON champions FOR SELECT
  TO authenticated
  USING (true);
```

#### Performance Metrics Table
```sql
-- Performance metrics table
CREATE TABLE performance_metrics (
  match_id TEXT PRIMARY KEY,
  participant_id INTEGER NOT NULL,
  kda DECIMAL,
  cs_per_min DECIMAL,
  gold_per_min DECIMAL,
  damage_per_min DECIMAL,
  vision_score INTEGER,
  kill_participation DECIMAL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;

-- Anyone authenticated can read
CREATE POLICY "Authenticated users can read metrics"
  ON performance_metrics FOR SELECT
  TO authenticated
  USING (true);
```

#### Performance Analysis Table
```sql
-- Performance analysis table
CREATE TABLE performance_analysis (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  match_id TEXT NOT NULL,
  summoner_id TEXT NOT NULL,
  overall_grade TEXT,
  metrics JSONB,
  phase_analysis JSONB,
  strengths TEXT[],
  weaknesses TEXT[],
  recommendations TEXT[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(match_id, summoner_id)
);

-- Enable RLS
ALTER TABLE performance_analysis ENABLE ROW LEVEL SECURITY;

-- Users can read their own analysis
CREATE POLICY "Users can read own analysis"
  ON performance_analysis FOR SELECT
  TO authenticated
  USING (true);
```

### 4. Enable Authentication

1. Go to **Authentication** → **Providers**
2. Enable **Email** provider
3. (Optional) Configure email templates
4. (Optional) Enable other providers (Google, GitHub, etc.)

### 5. Test Connection

Run this in your backend:

```bash
cd backend
python -c "from config.firebase import supabase_service; print('Connected!' if supabase_service.client else 'Failed')"
```

## 🔐 Authentication Flow

### Register User
```python
# Supabase handles this automatically
auth_response = client.auth.sign_up({
    "email": email,
    "password": password
})
```

### Login User
```python
auth_response = client.auth.sign_in_with_password({
    "email": email,
    "password": password
})
```

### Verify Token
```python
user = client.auth.get_user(token)
```

## 📊 Database Schema Overview

```
users
├── id (UUID, PK)
├── email (TEXT)
├── summoner_name (TEXT)
├── region (TEXT)
└── created_at (TIMESTAMP)

summoners
├── id (TEXT, PK)
├── user_id (UUID, FK → users)
├── summoner_name (TEXT)
├── region (TEXT)
├── puuid (TEXT)
├── summoner_level (INTEGER)
└── profile_icon_id (INTEGER)

match_timelines
├── match_id (TEXT, PK)
├── frames (JSONB)
└── frame_interval (INTEGER)

champions
├── id (TEXT, PK)
├── name (TEXT)
├── title (TEXT)
├── tags (TEXT[])
├── stats (JSONB)
└── abilities (JSONB)

performance_metrics
├── match_id (TEXT, PK)
├── participant_id (INTEGER)
├── kda (DECIMAL)
├── cs_per_min (DECIMAL)
├── gold_per_min (DECIMAL)
├── damage_per_min (DECIMAL)
├── vision_score (INTEGER)
└── kill_participation (DECIMAL)

performance_analysis
├── id (UUID, PK)
├── match_id (TEXT)
├── summoner_id (TEXT)
├── overall_grade (TEXT)
├── metrics (JSONB)
├── phase_analysis (JSONB)
├── strengths (TEXT[])
├── weaknesses (TEXT[])
└── recommendations (TEXT[])
```

## 🔒 Row Level Security (RLS)

Supabase uses RLS to secure your data:

- **Users**: Can only read/update their own data
- **Summoners**: Can only access their own linked accounts
- **Match Timelines**: Public read for all authenticated users
- **Champions**: Public read for all authenticated users
- **Performance Metrics**: Public read for all authenticated users
- **Performance Analysis**: All authenticated users can read

## 🛠️ Useful Supabase Features

### Real-time Subscriptions
```python
# Listen to changes in real-time
supabase.table('summoners').on('INSERT', handle_new_summoner).subscribe()
```

### Storage (for profile pictures, etc.)
```python
# Upload file
supabase.storage.from_('avatars').upload('user-id/avatar.png', file)
```

### Edge Functions (serverless)
Deploy Python/TypeScript functions that run on Supabase edge network.

## 📝 Migration from Firebase

Key differences:
- **Auth**: Supabase uses JWT tokens (similar to Firebase)
- **Database**: PostgreSQL (relational) vs Firestore (NoSQL)
- **Queries**: SQL-based vs document-based
- **RLS**: Built-in security policies vs Firebase rules

## 🚨 Common Issues

### Issue: "relation does not exist"
**Solution**: Make sure you ran all the CREATE TABLE commands

### Issue: "JWT expired"
**Solution**: Tokens expire after 1 hour by default. Refresh the token:
```python
client.auth.refresh_session()
```

### Issue: "Row Level Security policy violation"
**Solution**: Check your RLS policies match your use case

## 📚 Resources

- [Supabase Docs](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [SQL Tutorial](https://supabase.com/docs/guides/database)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)

## ✅ Checklist

- [ ] Created Supabase project
- [ ] Copied credentials to `.env`
- [ ] Created all database tables
- [ ] Enabled Row Level Security policies
- [ ] Enabled Email authentication
- [ ] Tested connection from backend
- [ ] Ready to go! 🚀
