# Rift Rewind - Clean Architecture Documentation

## 🎯 Overview

Rift Rewind backend follows **Clean Architecture** principles with strict separation of concerns:
- **Testability** - Each layer can be tested in isolation
- **Maintainability** - Clear boundaries and responsibilities
- **Flexibility** - Easy to swap implementations (Supabase → PostgreSQL)
- **Scalability** - Independent layer development

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                      Routes Layer                            │
│                 (HTTP Request/Response)                      │
└──────────────────────┬───────────────────────────────────────┘
                       │ Depends()
┌──────────────────────┴───────────────────────────────────────┐
│                    Services Layer                            │
│              (Business Logic Orchestration)                  │
└──────────┬──────────────────────────┬────────────────────────┘
           │                          │
    ┌──────┴──────┐          ┌────────┴────────┐
    │   Domain    │          │  Repositories   │
    │  (Business  │          │  (Interfaces)   │
    │   Rules)    │          └────────┬────────┘
    └─────────────┘                   │
                              ┌────────┴────────┐
                              │ Infrastructure  │
                              │ (Implementations│
                              │  + Database)    │
                              └─────────────────┘
```

---

## Layer 1: Routes (`routes/`)

**Responsibility**: Handle HTTP requests and responses ONLY

**Rules**:
- ❌ NO business logic
- ❌ NO database access
- ❌ NO validation (use Pydantic models)
- ✅ Extract data from requests
- ✅ Call services via dependency injection
- ✅ Return HTTP responses

**Example**:
```python
@router.post("/summoner", response_model=SummonerResponse)
async def link_summoner(
    summoner_request: SummonerRequest,
    current_user: str = Depends(get_current_user),
    player_service: PlayerService = Depends(get_player_service)
):
    """Link League account - delegates everything to service"""
    return await player_service.link_summoner(current_user, summoner_request)
```

---

## Layer 2: Services (`services/`)

**Responsibility**: Orchestrate operations between domain and repositories

**Rules**:
- ❌ NO business validation (use domain)
- ❌ NO direct database/API calls (use repositories)
- ✅ Coordinate operations
- ✅ Catch domain exceptions → convert to HTTPExceptions
- ✅ Validate repository responses
- ✅ Handle error cases

**Example**:
```python
class PlayerService:
    def __init__(self, player_repository: PlayerRepository, player_domain: PlayerDomain):
        self.player_repository = player_repository
        self.player_domain = player_domain
    
    async def link_summoner(self, user_id: str, request: SummonerRequest):
        # 1. Validate with domain (catches DomainException)
        try:
            self.player_domain.validate_region(request.region)
        except DomainException as e:
            raise HTTPException(status_code=400, detail=e.message)
        
        # 2. Fetch from repository
        summoner = await self.player_repository.get_summoner_by_riot_id(...)
        if not summoner:
            raise HTTPException(status_code=404, detail="Summoner not found")
        
        # 3. Save via repository
        result = await self.player_repository.save_summoner(user_id, data)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to save")
        
        return result
```

---

## Layer 3: Domain (`domain/`)

**Responsibility**: Pure business logic and validation rules

**Rules**:
- ❌ NO external dependencies (no database, no APIs, no HTTP)
- ❌ NO HTTPException (use custom domain exceptions)
- ✅ Pure functions
- ✅ Business validation
- ✅ Calculations
- ✅ Framework-agnostic

**Domain Exceptions** (`domain/exceptions.py`):
```python
class DomainException(Exception):
    """Base for all domain violations"""
    pass

class ValidationError(DomainException):
    """Validation rule violation"""
    pass

class InvalidRegionError(ValidationError):
    """Invalid region"""
    pass
```

**Example**:
```python
class PlayerDomain:
    def validate_region(self, region: str) -> None:
        """Pure business rule - no HTTP concerns"""
        valid_regions = ["americas", "europe", "asia", "sea"]
        if region not in valid_regions:
            raise InvalidRegionError(f"Region must be one of: {valid_regions}")
    
    def calculate_win_rate(self, wins: int, losses: int) -> float:
        """Pure calculation"""
        total = wins + losses
        return round((wins / total) * 100, 2) if total > 0 else 0.0
```

---

## Layer 4: Repositories - Interfaces (`repositories/`)

**Responsibility**: Define contracts for data access

**Rules**:
- ✅ Abstract base classes (ABC)
- ✅ Define method signatures
- ✅ Return types: `Optional[T]` for operations that can fail
- ❌ NO implementation details

**Example**:
```python
class PlayerRepository(ABC):
    @abstractmethod
    async def get_summoner_by_riot_id(
        self, game_name: str, tag_line: str, region: str
    ) -> Optional[SummonerResponse]:
        """Get summoner data, or None if not found"""
        pass
    
    @abstractmethod
    async def save_summoner(
        self, user_id: str, summoner_data: dict
    ) -> Optional[SummonerResponse]:
        """Save summoner data, or None if failed"""
        pass
```

---

## Layer 5: Infrastructure (`infrastructure/`)

**Responsibility**: Implement repository interfaces with external dependencies

**Rules**:
- ❌ NO HTTPException (return None on failure)
- ❌ NO business logic
- ❌ NO validation
- ✅ Talk to databases/APIs
- ✅ Return data or None
- ✅ Convert external data to domain models

**Example**:
```python
class PlayerRepositoryRiot(PlayerRepository):
    def __init__(self, client: DatabaseClient, riot_api_key: str):
        self.client = client
        self.riot_api_key = riot_api_key
    
    async def get_summoner_by_riot_id(self, game_name, tag_line, region):
        """Just fetch data - no validation, no exceptions"""
        if self.client:
            # Call Riot API (demo)
            return SummonerResponse(
                id=f"demo_{game_name}",
                summoner_name=f"{game_name}#{tag_line}",
                ...
            )
        return None
    
    async def save_summoner(self, user_id, summoner_data):
        """Just save data - no validation, no exceptions"""
        if self.client:
            self.client.table('summoners').upsert(summoner_data).execute()
            return SummonerResponse(**summoner_data)
        return None
```

---

## Layer 6: Database Abstraction (`infrastructure/database/`)

**Responsibility**: Abstract database operations for easy swapping

**Interface** (`database_client.py`):
```python
class DatabaseClient(ABC):
    """Abstract database operations"""
    
    @abstractmethod
    def table(self, table_name: str) -> TableQuery:
        pass
    
    @abstractmethod
    def auth_sign_up(self, email: str, password: str) -> AuthResponse:
        pass
    
    @abstractmethod
    def auth_sign_in(self, email: str, password: str) -> AuthResponse:
        pass
```

**Implementation** (`supabase_client.py`):
```python
class SupabaseClient(DatabaseClient):
    """Supabase implementation - wraps Supabase SDK"""
    
    def __init__(self, supabase_client):
        self._client = supabase_client
    
    def table(self, table_name: str) -> SupabaseTableQuery:
        return SupabaseTableQuery(self._client.table(table_name))
    
    def auth_sign_up(self, email, password):
        response = self._client.auth.sign_up({"email": email, "password": password})
        return AuthResponse(user=..., session=...)
```

**Benefits**:
- Swap Supabase → PostgreSQL by creating `PostgresClient`
- Repositories don't know about Supabase
- Easy to mock for testing

---

## 🔌 Dependency Injection (`dependency/dependencies.py`)

**Purpose**: Wire everything together cleanly

```python
# Domain Factories (no dependencies)
def get_player_domain() -> PlayerDomain:
    return PlayerDomain()

# Repository Factories (receive DatabaseClient)
def get_player_repository() -> PlayerRepository:
    return PlayerRepositoryRiot(supabase_service, settings.RIOT_API_KEY)

# Service Factories (receive repository + domain)
def get_player_service() -> PlayerService:
    return PlayerService(
        player_repository=get_player_repository(),
        player_domain=get_player_domain()
    )
```

**Usage in Routes**:
```python
@router.post("/summoner")
async def link_summoner(
    request: SummonerRequest,
    player_service: PlayerService = Depends(get_player_service)  # ✅ Injected
):
    return await player_service.link_summoner(...)
```

---

## 📊 Complete Data Flow Example

### Link League Account Flow:

```
1. CLIENT
   POST /api/players/summoner
   { "game_name": "Faker", "tag_line": "T1", "region": "americas" }
   ↓

2. ROUTE (routes/players.py)
   - Pydantic validates request model
   - Extracts current_user from JWT (middleware)
   - Injects PlayerService via Depends()
   - Calls: player_service.link_summoner(user_id, request)
   ↓

3. SERVICE (services/player_service.py)
   - Validates region via domain.validate_region()
   - Catches DomainException → converts to HTTPException
   - Calls: repository.get_summoner_by_riot_id()
   - Checks if result is None → raises HTTPException
   - Calls: repository.save_summoner()
   - Checks if result is None → raises HTTPException
   - Returns: SummonerResponse
   ↓

4. DOMAIN (domain/player_domain.py)
   - Validates region is in valid list
   - Raises InvalidRegionError if invalid
   - NO HTTP concerns, NO database access
   ↓

5. REPOSITORY (infrastructure/player_repository.py)
   - Calls Riot API via DatabaseClient
   - Converts response to SummonerResponse
   - Returns data or None (NO exceptions)
   ↓

6. DATABASE CLIENT (infrastructure/database/supabase_client.py)
   - Wraps Supabase SDK
   - Executes database operations
   - Returns raw data
   ↓

7. RESPONSE
   Returns SummonerResponse to client with 201 status
```

---

## 🎯 Key Architectural Rules

### ✅ DO:
- Routes → Services (via Depends)
- Services → Domain + Repositories
- Repositories → Database Client
- Domain → Pure logic (no dependencies)
- Return `Optional[T]` from repositories
- Throw domain exceptions in domain layer
- Convert domain exceptions to HTTP in services

### ❌ DON'T:
- Routes → Domain/Repositories directly
- Domain → External dependencies
- Repositories → HTTPException
- Services → Direct database access
- Mix HTTP concerns with business logic

---

## 🧪 Testing Strategy

### Unit Tests - Domain Layer
```python
def test_validate_region():
    domain = PlayerDomain()
    
    # Valid region
    domain.validate_region("americas")  # Should not raise
    
    # Invalid region
    with pytest.raises(InvalidRegionError):
        domain.validate_region("invalid")
```

### Unit Tests - Service Layer (Mock Repository)
```python
async def test_link_summoner():
    mock_repo = Mock(PlayerRepository)
    mock_repo.get_summoner_by_riot_id.return_value = SummonerResponse(...)
    mock_repo.save_summoner.return_value = SummonerResponse(...)
    
    service = PlayerService(mock_repo, PlayerDomain())
    result = await service.link_summoner("user123", request)
    
    assert result.summoner_name == "Faker#T1"
```

### Integration Tests - Full Stack
```python
async def test_link_summoner_endpoint(client):
    response = await client.post(
        "/api/players/summoner",
        json={"game_name": "Faker", "tag_line": "T1", "region": "americas"},
        headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 201
```

---

## 🚀 Adding a New Feature

1. **Create Models** (`models/feature.py`)
   - Request/Response Pydantic models

2. **Create Domain** (`domain/feature_domain.py`)
   - Business validation rules
   - Pure calculations
   - Custom domain exceptions

3. **Create Repository Interface** (`repositories/feature_repository.py`)
   - Abstract methods with `Optional[T]` returns

4. **Create Infrastructure** (`infrastructure/feature_repository.py`)
   - Implement interface
   - Use `DatabaseClient`
   - Return data or None

5. **Create Service** (`services/feature_service.py`)
   - Orchestrate domain + repository
   - Catch domain exceptions → HTTPException
   - Validate repository responses

6. **Create Routes** (`routes/feature.py`)
   - HTTP endpoints
   - Use `Depends()` for service injection

7. **Add Factories** (`dependency/dependencies.py`)
   - Domain, repository, service factories

8. **Register Router** (`main.py`)
   - `app.include_router(feature_router)`

---

## 📚 Benefits of This Architecture

### 1. Testability
- Mock `DatabaseClient` for repository tests
- Mock repositories for service tests
- Test domain logic with zero dependencies

### 2. Maintainability
- Bug in validation? Check `domain/`
- Database error? Check `infrastructure/`
- HTTP issue? Check `routes/`

### 3. Flexibility
- Swap Supabase → PostgreSQL (change `DatabaseClient` implementation)
- Swap Riot API client (change repository implementation)
- Change validation rules (modify domain only)

### 4. Scalability
- Parallel development on different layers
- Add features without touching existing code
- Clear boundaries prevent coupling

---

## 📖 Further Reading

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
