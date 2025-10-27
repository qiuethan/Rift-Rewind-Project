# Rift Rewind - Clean Architecture Documentation

## 🎯 Overview

Rift Rewind is a League of Legends analytics platform built with **Clean Architecture** principles, ensuring:
- **Testability** - Easy to mock and test each layer
- **Maintainability** - Clear separation of concerns
- **Flexibility** - Easy to swap implementations
- **Scalability** - Clean boundaries between layers

## 🏗️ Architecture Layers

### Layer 1: Routes (API/Presentation Layer)
**Location**: `routes/`

**Responsibility**: Handle HTTP requests and responses only

**Rules**:
- NO business logic
- NO database access
- Only HTTP concerns (status codes, headers, response models)
- Delegate everything to services

**Example**:
```python
@router.post("/summoner", response_model=SummonerResponse)
async def link_summoner(
    summoner_request: SummonerRequest,
    current_user: str = Depends(get_current_user),
    player_service: PlayerService = Depends(get_player_service)
):
    return await player_service.link_summoner(current_user, summoner_request)
```

### Layer 2: Services (Use Cases/Application Layer)
**Location**: `services/`

**Responsibility**: Orchestrate between domain and infrastructure

**Rules**:
- NO business logic (that goes in domain)
- NO direct database/API access (use repositories)
- Pure orchestration - coordinate operations
- Always async methods

**Example**:
```python
class PlayerService:
    def __init__(self, player_repository: PlayerRepository, player_domain: PlayerDomain):
        self.player_repository = player_repository
        self.player_domain = player_domain
    
    async def link_summoner(self, user_id: str, summoner_request: SummonerRequest):
        # 1. Validate (domain)
        self.player_domain.validate_summoner_name(summoner_request.summoner_name)
        
        # 2. Fetch data (infrastructure)
        summoner = await self.player_repository.get_summoner_by_name(...)
        
        # 3. Save (infrastructure)
        return await self.player_repository.save_summoner(user_id, summoner_data)
```

### Layer 3: Domain (Business Logic Layer)
**Location**: `domain/`

**Responsibility**: Pure business logic and validation rules

**Rules**:
- NO external dependencies (no Firebase, no APIs, no database)
- Pure functions and business rules
- Can raise HTTPException for validation errors
- Easy to test in isolation

**Example**:
```python
class PlayerDomain:
    def validate_summoner_name(self, name: str) -> None:
        if not name or len(name.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Summoner name must be at least 3 characters"
            )
    
    def calculate_win_rate(self, wins: int, losses: int) -> float:
        total_games = wins + losses
        if total_games == 0:
            return 0.0
        return round((wins / total_games) * 100, 2)
```

### Layer 4: Repositories (Abstract Interfaces/Ports)
**Location**: `repositories/`

**Responsibility**: Define contracts for data access

**Rules**:
- Abstract base classes (ABC)
- Define what operations are available
- NO implementation details
- Allow easy swapping of implementations

**Example**:
```python
class PlayerRepository(ABC):
    @abstractmethod
    async def get_summoner_by_name(self, summoner_name: str, region: str) -> Optional[SummonerResponse]:
        pass
    
    @abstractmethod
    async def save_summoner(self, user_id: str, summoner_data: dict) -> SummonerResponse:
        pass
```

### Layer 5: Infrastructure (Concrete Implementations/Adapters)
**Location**: `infrastructure/`

**Responsibility**: Implement repository interfaces with external dependencies

**Rules**:
- Implements repository interfaces
- Contains all external dependencies (Firebase, Riot API, LLM)
- Can be swapped out without changing business logic
- Handle errors and convert to domain models

**Example**:
```python
class PlayerRepositoryRiot(PlayerRepository):
    def __init__(self, db, riot_api_key: str):
        self.db = db
        self.riot_api_key = riot_api_key
    
    async def get_summoner_by_name(self, summoner_name: str, region: str):
        # Call Riot API
        # Handle errors
        # Convert to domain model
        return SummonerResponse(...)
    
    async def save_summoner(self, user_id: str, summoner_data: dict):
        # Save to Firebase
        # Handle errors
        return SummonerResponse(**summoner_data)
```

## 🔌 Dependency Injection

**Location**: `dependency/dependencies.py`

**Purpose**: Wire everything together cleanly

**Pattern**:
```python
# Factory functions
def get_player_domain() -> PlayerDomain:
    return PlayerDomain()

def get_player_repository() -> PlayerRepository:
    return PlayerRepositoryRiot(firebase_service.db, settings.RIOT_API_KEY)

def get_player_service() -> PlayerService:
    return PlayerService(
        player_repository=get_player_repository(),
        player_domain=get_player_domain()
    )
```

**Usage in Routes**:
```python
@router.get("/summoner")
async def get_summoner(
    player_service: PlayerService = Depends(get_player_service)
):
    return await player_service.get_summoner(...)
```

## 📊 Data Flow

### Example: Link Summoner Account

```
1. CLIENT
   POST /api/players/summoner
   { "summoner_name": "Faker", "region": "KR" }
   ↓

2. ROUTE (routes/players.py)
   - Validate request with Pydantic
   - Extract current_user from JWT
   - Inject PlayerService
   ↓

3. SERVICE (services/player_service.py)
   - Call domain.validate_summoner_name()
   - Call domain.validate_region()
   - Call repository.get_summoner_by_name()
   - Call repository.save_summoner()
   ↓

4. DOMAIN (domain/player_domain.py)
   - Validate summoner name length
   - Validate region is valid
   - Raise HTTPException if invalid
   ↓

5. INFRASTRUCTURE (infrastructure/player_repository.py)
   - Call Riot API to get summoner data
   - Save to Firebase
   - Convert to SummonerResponse model
   ↓

6. RESPONSE
   Returns SummonerResponse to client
```

## 🎨 Design Patterns

### 1. Repository Pattern
- Abstract data access behind interfaces
- Easy to swap implementations (Firebase → PostgreSQL)
- Easy to mock for testing

### 2. Dependency Injection
- Inject dependencies from outside
- No hard-coded dependencies
- Easy to test with mocks

### 3. Service Layer Pattern
- Orchestrate complex operations
- Keep routes thin
- Reusable business operations

### 4. Domain-Driven Design
- Business logic in domain layer
- Pure functions
- No external dependencies

## 📦 Models (Pydantic)

**Location**: `models/`

**Purpose**: Data validation and serialization

**Types**:
- **Request Models**: Validate incoming data
- **Response Models**: Structure outgoing data

**Example**:
```python
class SummonerRequest(BaseModel):
    summoner_name: str = Field(..., min_length=3, max_length=16)
    region: str = Field(..., pattern="^(NA1|EUW1|...)$")

class SummonerResponse(BaseModel):
    id: str
    summoner_name: str
    region: str
    puuid: str
    summoner_level: int
```

## 🔐 Authentication Flow

```
1. User registers/logs in
   ↓
2. AuthService creates user in Firebase
   ↓
3. Generate JWT token
   ↓
4. Return token to client
   ↓
5. Client includes token in Authorization header
   ↓
6. get_current_user middleware verifies token
   ↓
7. Extract user_id from token
   ↓
8. Pass user_id to route handler
```

## 🧪 Testing Strategy

### Unit Tests
- **Domain**: Test business logic in isolation
- **Services**: Mock repositories, test orchestration
- **Repositories**: Mock external APIs

### Integration Tests
- Test full request/response cycle
- Use test database
- Mock external APIs (Riot, OpenRouter)

### Example Test:
```python
def test_validate_summoner_name():
    domain = PlayerDomain()
    
    # Should pass
    domain.validate_summoner_name("ValidName")
    
    # Should raise exception
    with pytest.raises(HTTPException):
        domain.validate_summoner_name("ab")  # Too short
```

## 🚀 Adding a New Feature

### Step-by-Step Guide

1. **Create Models** (`models/feature.py`)
   - Request model
   - Response model

2. **Create Domain** (`domain/feature_domain.py`)
   - Business logic
   - Validation rules

3. **Create Repository Interface** (`repositories/feature_repository.py`)
   - Abstract methods

4. **Create Infrastructure** (`infrastructure/feature_repository.py`)
   - Implement repository interface
   - Handle external dependencies

5. **Create Service** (`services/feature_service.py`)
   - Orchestrate operations
   - Use domain and repository

6. **Create Route** (`routes/feature.py`)
   - HTTP endpoints
   - Use service

7. **Add Dependencies** (`dependency/dependencies.py`)
   - Factory functions

8. **Register Route** (`main.py`)
   - Include router

## 📚 Key Principles

### 1. Dependency Inversion
- High-level modules don't depend on low-level modules
- Both depend on abstractions (interfaces)

### 2. Single Responsibility
- Each class has one reason to change
- Routes handle HTTP, Services orchestrate, Domain validates

### 3. Open/Closed Principle
- Open for extension, closed for modification
- Add new features without changing existing code

### 4. Interface Segregation
- Clients shouldn't depend on interfaces they don't use
- Small, focused repository interfaces

### 5. Don't Repeat Yourself (DRY)
- Reuse domain logic across services
- Reuse repository implementations

## 🎯 Benefits

### Testability
- Mock repositories for service tests
- Test domain logic in isolation
- No database needed for unit tests

### Maintainability
- Clear separation of concerns
- Easy to find and fix bugs
- Self-documenting code structure

### Flexibility
- Swap Firebase for PostgreSQL
- Change Riot API client
- Add new features without breaking existing ones

### Scalability
- Add new features independently
- Parallel development on different layers
- Easy to refactor

## 🔍 Common Patterns

### Protected Route
```python
@router.get("/protected")
async def protected_route(
    current_user: str = Depends(get_current_user),
    service: Service = Depends(get_service)
):
    return await service.do_something(current_user)
```

### Public Route
```python
@router.get("/public")
async def public_route(
    service: Service = Depends(get_service)
):
    return await service.do_something()
```

### Error Handling
```python
# In domain
if not valid:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Validation error"
    )

# In infrastructure
try:
    result = await external_api.call()
except Exception as e:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"External API error: {str(e)}"
    )
```

## 📖 Further Reading

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Dependency Injection in Python](https://python-dependency-injector.ets-labs.org/)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
