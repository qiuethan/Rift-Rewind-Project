# Rift Rewind API

FastAPI backend for League of Legends player analytics and champion recommendations, built using Clean Architecture principles.

## 🏗️ Architecture

This project follows **Clean Architecture** with strict separation of concerns:

```
┌─────────────────┐
│     Routes      │  API endpoints & HTTP handling
└─────────────────┘
         ↓
┌─────────────────┐
│    Services     │  Use Cases - Pure orchestration
└─────────────────┘
         ↓
┌─────────────────┐
│     Domain      │  Business logic & validation rules
└─────────────────┘
         ↓
┌─────────────────┐
│ Infrastructure  │  Firebase, Riot API, external dependencies
└─────────────────┘
```

## 📁 Project Structure

```
backend/
├── routes/              # API endpoints (HTTP layer)
├── services/           # Use cases (orchestration)
├── domain/             # Business logic
├── repositories/       # Abstract interfaces
├── infrastructure/     # Concrete implementations
├── models/             # Pydantic models
├── middleware/         # Auth, error handling
├── dependency/         # Dependency injection
├── config/             # Configuration
├── utils/              # Utilities
└── main.py            # Application entry point
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Supabase project (for authentication and database)
- Riot API key (for League of Legends data)
- AWS account with Bedrock access (optional, for AI-powered analysis)

### Installation

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/verify` - Verify token
- `GET /api/auth/me` - Get current user

### Players
- `POST /api/players/summoner` - Link summoner account
- `GET /api/players/summoner` - Get linked summoner
- `GET /api/players/stats/{summoner_id}` - Get player stats
- `GET /api/players/matches` - Get match history

### Matches
- `GET /api/matches/{match_id}/timeline` - Get match timeline
- `GET /api/matches/{match_id}/summary` - Get match summary
- `GET /api/matches/{match_id}/participant/{id}` - Get participant data

### Champions
- `GET /api/champions/` - Get all champions
- `GET /api/champions/{champion_id}` - Get champion data
- `POST /api/champions/recommendations` - Get recommendations
- `POST /api/champions/similarity` - Calculate similarity

### Analytics
- `POST /api/analytics/performance` - Analyze performance
- `POST /api/analytics/progression` - Get skill progression
- `POST /api/analytics/insights` - Generate AI insights

### Health
- `GET /api/health/` - Health check
- `GET /api/health/ping` - Ping endpoint

## 🔒 Authentication

Protected endpoints require a Bearer token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/auth/me
```

## 🧪 Testing

Run tests with pytest:

```bash
pytest
pytest --cov=. --cov-report=html
```

## 📝 Environment Variables

See `.env.example` for all available configuration options.

Required variables:
- `FIREBASE_CREDENTIALS_PATH` - Path to Firebase credentials JSON
- `RIOT_API_KEY` - Your Riot Games API key
- `JWT_SECRET_KEY` - Secret key for JWT tokens

Optional variables:
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` - For AI-powered analysis with AWS Bedrock
- `DEBUG` - Enable debug mode

## 🏛️ Clean Architecture Principles

### Layers

1. **Routes** - Handle HTTP requests/responses only
2. **Services** - Orchestrate between domain and infrastructure
3. **Domain** - Pure business logic and validation
4. **Repositories** - Abstract data access interfaces
5. **Infrastructure** - Concrete implementations (Firebase, Riot API)

### Dependency Injection

All dependencies are injected via FastAPI's `Depends()`:

```python
@router.get("/example")
async def example(
    current_user: str = Depends(get_current_user),
    service: ExampleService = Depends(get_example_service)
):
    return await service.do_something(current_user)
```

## 🛠️ Development

### Code Style

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Adding a New Feature

1. Create models in `models/`
2. Create domain logic in `domain/`
3. Create repository interface in `repositories/`
4. Create infrastructure implementation in `infrastructure/`
5. Create service in `services/`
6. Create route in `routes/`
7. Add dependencies in `dependency/dependencies.py`
8. Register route in `main.py`

## 📄 License

MIT License

## 🤝 Contributing

1. Follow Clean Architecture principles
2. Add type hints to all functions
3. Write tests for new features
4. Update documentation
5. Follow existing code style

## 📧 Contact

For questions or issues, please open a GitHub issue.
