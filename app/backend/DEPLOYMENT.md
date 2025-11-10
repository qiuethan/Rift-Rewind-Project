# Fly.io Backend Deployment Guide

## Prerequisites
1. Install Fly.io CLI: https://fly.io/docs/hands-on/install-flyctl/
2. Sign up/login: `flyctl auth signup` or `flyctl auth login`

## Initial Setup

### 1. Navigate to the backend directory
```bash
cd app/backend
```

### 2. Launch the app (first time only)
```bash
flyctl launch
```
- Choose app name (or use default: rift-rewind-backend)
- Choose region (e.g., iad for US East)
- **Do NOT deploy yet** - we need to set secrets first

### 3. Set Environment Variables
```bash
# Set your secrets
flyctl secrets set RIOT_API_KEY="your-riot-api-key"
flyctl secrets set SUPABASE_URL="your-supabase-url"
flyctl secrets set SUPABASE_KEY="your-supabase-key"
flyctl secrets set JWT_SECRET_KEY="your-jwt-secret"
flyctl secrets set JWT_ALGORITHM="HS256"
flyctl secrets set ACCESS_TOKEN_EXPIRE_MINUTES="30"

# Optional: Set CORS origins for production
flyctl secrets set CORS_ORIGINS="https://your-frontend-domain.vercel.app,https://www.your-domain.com"
```

### 4. Deploy
```bash
flyctl deploy
```

## Subsequent Deployments
After initial setup, just run:
```bash
cd app/backend
flyctl deploy
```

## Monitoring & Management

### View logs
```bash
flyctl logs
```

### Check app status
```bash
flyctl status
```

### Open app in browser
```bash
flyctl open
```

### SSH into the machine
```bash
flyctl ssh console
```

### Scale the app
```bash
# Scale to 2 machines
flyctl scale count 2

# Change machine size
flyctl scale vm shared-cpu-1x --memory 512
```

## Database Migrations
If you need to run migrations:
```bash
flyctl ssh console
cd /app/app/backend
python -m database.run_migrations
```

## Troubleshooting

### Check if app is healthy
```bash
curl https://rift-rewind-backend.fly.dev/health
```

### View environment variables (without values)
```bash
flyctl secrets list
```

### Restart the app
```bash
flyctl apps restart rift-rewind-backend
```

## Cost Optimization
- The config uses `auto_stop_machines = true` and `min_machines_running = 0`
- This means the app will scale to zero when idle (free!)
- First request after idle will have ~1-2 second cold start

## Important Notes
1. The Dockerfile copies the entire monorepo, so backend can access shared resources
2. The app runs from `/app/app/backend` directory inside the container
3. Health check endpoint must be implemented at `/health` in your FastAPI app
4. CORS must be configured to allow your frontend domain

## Frontend Configuration
Update your frontend `.env` to point to the Fly.io backend:
```
VITE_API_BASE_URL=https://rift-rewind-backend.fly.dev
```
