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
│              (HTTP Request/Response Handling)                │
│                    Uses: Pydantic Models                     │
└──────────────────────┬───────────────────────────────────────┘
                       │ Depends()
┌──────────────────────┴───────────────────────────────────────┐
│                    Services Layer                            │
│              (Business Logic Orchestration)                  │
│         Converts: DomainException → HTTPException            │
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

Cross-Cutting Concerns:
┌─────────────────────────────────────────────────────────────┐
│  Models (Pydantic) - Data validation & serialization        │
│  Exceptions (Domain) - Business rule violations             │
│  Logger (Utils) - Structured logging                        │
│  Dependencies (DI) - Wiring everything together             │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer 0: Models (`models/`)

**Responsibility**: Define data structures and validation rules using Pydantic

**Rules**:
- ✅ Use Pydantic `BaseModel` for all models
- ✅ Define Request models for API inputs
- ✅ Define Response models for API outputs
- ✅ Use type hints for all fields
- ✅ Add validation with `Field()` constraints
- ✅ Keep models pure data structures (no business logic)
- ❌ NO business validation (use domain layer)
- ❌ NO database operations
- ❌ NO external API calls

**Model Categories**:

1. **Request Models** - API input validation
   ```python
   class SummonerRequest(BaseModel):
       """Request model for linking summoner account"""
       summoner_name: Optional[str] = None
       game_name: Optional[str] = None
       tag_line: Optional[str] = None
       region: str
       
       class Config:
           extra = "forbid"  # Reject unknown fields
   ```

2. **Response Models** - API output structure
   ```python
   class SummonerResponse(BaseModel):
       """Response model for summoner data"""
       puuid: str
       summoner_name: str
       game_name: Optional[str] = None
       tag_line: Optional[str] = None
       region: str
       summoner_level: int
       profile_icon_id: int
       champion_masteries: Optional[List[dict]] = None
       top_champions: Optional[List[dict]] = None
       recent_games: Optional[List[dict]] = None
       
       class Config:
           extra = "allow"  # Allow additional fields
   ```

3. **Database Models** - Internal data structures
   ```python
   class SummonerRecord(BaseModel):
       """Database record for summoner table"""
       puuid: str
       summoner_id: Optional[str] = None
       summoner_name: str
       region: str
       
       @classmethod
       def from_summoner_data(cls, summoner_data: dict) -> 'SummonerRecord':
           """Create from dictionary"""
           return cls(**summoner_data)
       
       def to_db_dict(self) -> dict:
           """Convert to database dictionary"""
           return self.dict(exclude_none=False)
   ```

4. **External API Models** - Third-party API responses
   ```python
   class AccountResponse(BaseModel):
       """Response from Riot Account API"""
       puuid: str
       game_name: str = Field(alias="gameName")
       tag_line: str = Field(alias="tagLine")
       
       class Config:
           populate_by_name = True  # Accept both snake_case and camelCase
   ```

**Current Model Files**:
- `models/auth.py` - Authentication (RegisterRequest, LoginRequest, AuthResponse)
- `models/players.py` - Player/Summoner (SummonerRequest, SummonerResponse, PlayerStatsResponse)
- `models/matches.py` - Match data (MatchRequest, MatchTimelineResponse, MatchSummaryResponse)
- `models/champions.py` - Champions (ChampionRecommendationRequest, ChampionSimilarityRequest)
- `models/analytics.py` - Analytics (PerformanceAnalysisRequest, SkillProgressionRequest)
- `models/riot_api.py` - Riot API responses (AccountResponse, SummonerAPIResponse, ChampionMasteryResponse)

**Best Practices**:
- Use `Optional[T]` for nullable fields
- Use `Field()` for validation constraints (min_length, max_length, ge, le)
- Use `alias` for API field name mapping (camelCase ↔ snake_case)
- Set `extra = "forbid"` for strict Request models
- Set `extra = "allow"` for flexible Response models
- Add docstrings to all models
- Group related models in the same file

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
    """Base exception for domain violations"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ValidationError(DomainException):
    """Validation rule violation"""
    pass

class InvalidRegionError(ValidationError):
    """Invalid region"""
    pass

class InvalidSummonerNameError(ValidationError):
    """Invalid summoner name"""
    pass

class InvalidMatchIdError(ValidationError):
    """Invalid match ID"""
    pass

class InvalidChampionIdError(ValidationError):
    """Invalid champion ID"""
    pass

class InvalidTimeRangeError(ValidationError):
    """Invalid time range"""
    pass

class InvalidEmailError(ValidationError):
    """Invalid email format"""
    pass

class InvalidPasswordError(ValidationError):
    """Invalid password"""
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
    def __init__(self, db: DatabaseClient, riot_api: RiotAPIRepository):
        """
        Initialize repository with injected dependencies
        
        Args:
            db: Database abstraction for data persistence
            riot_api: Riot API repository for external API calls
        """
        self.db = db
        self.riot_api = riot_api
    
    async def get_summoner_by_riot_id(self, game_name, tag_line, region):
        """Fetch data from Riot API - no validation, returns None on failure"""
        try:
            # Step 1: Get account (PUUID) from Riot ID
            account_data = await self.riot_api.get_account_by_riot_id(
                game_name, tag_line, region
            )
            if not account_data:
                return None
            
            # Step 2: Get summoner data by PUUID
            summoner_data = await self.riot_api.get_summoner_by_puuid(
                account_data['puuid'], region
            )
            
            return SummonerResponse(**summoner_data) if summoner_data else None
        except Exception as e:
            logger.error(f"Error fetching summoner: {e}")
            return None
    
    async def save_summoner(self, user_id, summoner_data):
        """Save data to database - no validation, returns None on failure"""
        try:
            result = self.db.table('user_summoners').upsert({
                'user_id': user_id,
                **summoner_data
            }).execute()
            return SummonerResponse(**summoner_data) if result else None
        except Exception as e:
            logger.error(f"Error saving summoner: {e}")
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
    return PlayerRepositoryRiot(supabase_service, get_riot_api_repository())

# Service Factories (receive repository + domain)
def get_player_service() -> PlayerService:
    return PlayerService(
        player_repository=get_player_repository(),
        player_domain=get_player_domain()
    )

# LLM Service Factory (config injected via DI)
def get_bedrock_service() -> BedrockService:
    return BedrockService(
        aws_access_key=settings.AWS_ACCESS_KEY_ID,
        aws_secret_key=settings.AWS_SECRET_ACCESS_KEY,
        region=settings.AWS_REGION,
        model_id=settings.AWS_BEDROCK_MODEL
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
- Routes → Services (via `Depends()`)
- Services → Domain + Repositories
- Services wrap domain calls in try-catch blocks
- Services convert `DomainException` → `HTTPException`
- Repositories → Database Client or External APIs
- Repositories return `Optional[T]` (data or `None`)
- Domain → Pure logic (no external dependencies)
- Domain raises custom domain exceptions
- Infrastructure logs errors and returns `None` on failure
- Inject config values via dependency injection

### ❌ DON'T:
- Routes → Domain/Repositories directly
- Domain → Import FastAPI, HTTPException, or any framework
- Domain → Import database, Supabase, or external services
- Repositories → Raise `HTTPException`
- Services → Import from `infrastructure/`
- Services → Import from `config/` (use DI instead)
- Services → Direct database access
- Infrastructure → Raise `HTTPException`
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
   - **Request Models**: Define input validation with `Field()` constraints
   - **Response Models**: Define output structure with proper types
   - **Database Models**: Add helper methods like `from_dict()` and `to_db_dict()`
   - Set `extra = "forbid"` for Request models (strict validation)
   - Set `extra = "allow"` for Response models (flexibility)
   - Add comprehensive docstrings

2. **Create Domain Exceptions** (`domain/exceptions.py`)
   - Add custom exceptions for your feature
   - Inherit from `DomainException` or `ValidationError`

3. **Create Domain** (`domain/feature_domain.py`)
   - Business validation rules (raise domain exceptions)
   - Pure calculations (no side effects)
   - Framework-agnostic logic

4. **Create Repository Interface** (`repositories/feature_repository.py`)
   - Abstract base class inheriting from `ABC`
   - Abstract methods with `Optional[T]` returns
   - Clear method signatures and docstrings

5. **Create Infrastructure** (`infrastructure/feature_repository.py`)
   - Implement repository interface
   - Use `DatabaseClient` for database operations
   - Return data or `None` on failure (no exceptions)
   - Log errors with `logger`

6. **Create Service** (`services/feature_service.py`)
   - Import `DomainException` from `domain.exceptions`
   - Orchestrate domain + repository calls
   - Wrap domain validations in try-catch blocks
   - Convert `DomainException` → `HTTPException`
   - Validate repository responses (check for `None`)

7. **Create Routes** (`routes/feature.py`)
   - HTTP endpoints with proper status codes
   - Use `Depends()` for service injection
   - Use `Depends(get_current_user)` for auth
   - Pydantic models for request/response validation

8. **Add Factories** (`dependency/dependencies.py`)
   - Domain factory (no dependencies)
   - Repository factory (inject database client)
   - Service factory (inject repository + domain)

9. **Register Router** (`main.py`)
   - `app.include_router(feature_router)`
   - Add appropriate prefix and tags

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
