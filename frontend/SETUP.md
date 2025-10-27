# Frontend Setup Guide

## 📦 Installation

```bash
cd frontend
npm install
```

## 🔧 Configuration

### 1. Create .env file
```bash
cp .env.example .env
```

### 2. Add Supabase Credentials

Get these from your Supabase project dashboard:

```env
VITE_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
VITE_API_BASE_URL=http://localhost:8000
```

**Where to find these:**
1. Go to [supabase.com](https://supabase.com)
2. Open your project
3. Go to **Settings** → **API**
4. Copy:
   - **Project URL** → `VITE_SUPABASE_URL`
   - **anon public** key → `VITE_SUPABASE_ANON_KEY`

## 🚀 Run Development Server

```bash
npm run dev
```

Frontend will be available at: http://localhost:5173

## 🔗 Connect to Backend

Make sure your backend is running on port 8000:

```bash
cd ../backend
python main.py
```

The frontend will proxy `/api/*` requests to `http://localhost:8000`

## ✅ Test Authentication

1. Visit http://localhost:5173
2. Click "Sign up"
3. Register with email/password
4. You should be redirected to the dashboard

## 🎯 What's Working

- ✅ Supabase authentication (register/login)
- ✅ JWT token storage
- ✅ Protected routes
- ✅ Auto-injected auth headers
- ✅ Clean architecture (Pages → Actions → API)

## 🐛 Troubleshooting

### "Cannot find module" errors
```bash
npm install
```

### Supabase connection errors
- Check your `.env` file has correct credentials
- Verify Supabase project is active
- Check browser console for specific errors

### Backend connection errors
- Make sure backend is running on port 8000
- Check `VITE_API_BASE_URL` in `.env`
- Verify CORS is enabled in backend

### TypeScript errors
These are expected before running `npm install`. They'll disappear after installation.

## 📝 Next Steps

1. **Test the flow:**
   - Register a new user
   - Login
   - View dashboard

2. **Add more pages:**
   - Profile page
   - Analytics page
   - Champions page

3. **Customize:**
   - Update colors in `index.css`
   - Add your branding
   - Modify components

## 🎨 File Structure

```
frontend/
├── src/
│   ├── api/              # HTTP layer
│   │   ├── client.ts     # Axios instance (DO NOT MODIFY)
│   │   ├── auth.ts       # Auth API calls
│   │   ├── players.ts    # Player API calls
│   │   ├── champions.ts  # Champion API calls
│   │   └── analytics.ts  # Analytics API calls
│   │
│   ├── actions/          # Business logic
│   │   ├── auth.ts       # Auth actions (uses Supabase)
│   │   ├── players.ts    # Player actions
│   │   ├── champions.ts  # Champion actions
│   │   └── analytics.ts  # Analytics actions
│   │
│   ├── components/       # Reusable components
│   │   ├── Button/
│   │   ├── Input/
│   │   └── Card/
│   │
│   ├── pages/            # Route pages
│   │   ├── LoginPage/
│   │   ├── RegisterPage/
│   │   └── DashboardPage/
│   │
│   ├── config/           # Configuration
│   │   └── constants.ts  # API URLs, routes, storage keys
│   │
│   ├── lib/              # Third-party integrations
│   │   └── supabase.ts   # Supabase client
│   │
│   ├── App.tsx           # Routes
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
│
├── .env                  # Environment variables (create this)
├── .env.example          # Environment template
├── package.json          # Dependencies
├── vite.config.ts        # Vite configuration
└── tsconfig.json         # TypeScript configuration
```

## 🔐 Authentication Flow

```
1. User enters email/password
   ↓
2. authActions.register() or authActions.login()
   ↓
3. Supabase creates user & returns session
   ↓
4. Token stored in localStorage
   ↓
5. User redirected to dashboard
   ↓
6. All API calls include token automatically
```

## 📖 Documentation

- See `README.md` for detailed usage
- Check `../backend/SUPABASE_SETUP.md` for database setup
- Review code comments for implementation details

## ✨ You're All Set!

Your frontend is ready to go. Just:
1. `npm install`
2. Configure `.env`
3. `npm run dev`
4. Start building! 🚀
