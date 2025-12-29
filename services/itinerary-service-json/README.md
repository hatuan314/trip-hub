# Itinerary Service

**Itinerary Service** quản lý lịch trình du lịch (itineraries) và các hoạt động (activities) trong lịch trình của người dùng. Service lưu trữ dữ liệu trong **PostgreSQL** và cung cấp authentication thông qua JWT.

---

## 📋 Mục Lục

1. [Phân Tích Yêu Cầu](#phân-tích-yêu-cầu)
2. [Thiết Kế Phần Mềm](#thiết-kế-phần-mềm)
3. [API Endpoints](#api-endpoints)
4. [Giải Thích Hoạt Động](#giải-thích-hoạt-động)
5. [Cấu Hình và Triển Khai](#cấu-hình-và-triển-khai)

---

## 📌 Phân Tích Yêu Cầu

Service cung cấp các chức năng chính sau, bám sát theo implementation hiện có:

### 1. **User Authentication**

**Yêu cầu**:
- User registration với username và password
- User login phát hành JWT token
- JWT token có expiration time (1 hour)
- Password storage trong PostgreSQL database
- Shared user table với middleware-service

**Implementation**:
- JWT với HS256 algorithm
- Secret key: "SECRET" (hardcoded)
- **Security Warning**: Passwords stored in **plain text** (not hashed!)

### 2. **Itinerary Management**

**Yêu cầu**:
- Tạo itinerary mới cho user
- List tất cả itineraries của user
- Mỗi itinerary có:
  - Unique ID (UUID)
  - Title
  - Start date & End date
  - Description
  - Owner (username)
  - Created timestamp

**Data Model**:
- PostgreSQL table: `itineraries`
- UUID primary key
- User ownership tracking
- Date range validation (start_date → end_date)

### 3. **Activity Management**

**Yêu cầu**:
- Tạo activity trong một itinerary
- List tất cả activities của một itinerary
- Mỗi activity có:
  - Unique ID (UUID)
  - Itinerary ID (foreign reference)
  - Title
  - Start time & End time (datetime)
  - Location
  - Optional note
  - Owner (username)

**Business Rules**:
- Activity phải belong to một itinerary
- Activity có time range (start_time → end_time)
- Owner verification (user chỉ xem được activities của mình)

### 4. **Data Persistence**

**Yêu cầu**:
- PostgreSQL database cho persistent storage
- Shared database với middleware-service (`trip_hub`)
- Automatic table creation on startup
- Transaction support với SQLAlchemy ORM

**Tables**:
1. `users` - User authentication (shared)
2. `itineraries` - Travel itineraries
3. `activities` - Activities within itineraries

---

## 🏗️ Thiết Kế Phần Mềm

Service được thiết kế theo **Repository Pattern** với PostgreSQL:

```
src/
├── main.py                          # Entry point, FastAPI app
├── config/
│   └── settings.py                  # Configuration (database URL)
├── api/
│   └── v1/
│       ├── router.py                # Router aggregation
│       ├── dependencies.py          # JWT auth & DB session
│       └── endpoints/
│           ├── auth.py              # Register/Login
│           ├── itineraries.py       # Itinerary CRUD
│           └── activities.py        # Activity CRUD
├── infrastructure/
│   ├── database/
│   │   ├── connection.py            # SQLAlchemy setup
│   │   └── models.py                # ORM models
│   ├── user_repo.py                 # User repository
│   ├── itinerary_repo.py            # Itinerary repository
│   └── activity_repo.py             # Activity repository
├── schemas/
│   ├── auth.py                      # Auth Pydantic schemas
│   ├── itinerary.py                 # Itinerary schemas
│   └── activity.py                  # Activity schemas
└── utils/
    ├── security.py                  # JWT & password handling
    └── json_storage.py              # JSON file I/O (not used)
```

### Kiến Trúc Chi Tiết

#### **1. Main Application** (`main.py`)

**Khởi tạo FastAPI**:
```python
app = FastAPI(title="Itinerary Service")
```

**Startup Event**:
```python
@app.on_event("startup")
def on_startup():
    init_db()  # Create tables if not exist
```

**Router Registration**:
- `/api/v1/auth` - Authentication endpoints
- `/api/v1/itineraries` - Itinerary management
- `/api/v1/activities` - Activity management

#### **2. Database Models** (`infrastructure/database/models.py`)

**User Model**:
```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int]
    username: Mapped[str]  # unique, indexed
    password: Mapped[str]  # plain text!
    created_at: Mapped[datetime]
```

**Itinerary Model**:
```python
class Itinerary(Base):
    __tablename__ = "itineraries"
    
    id: Mapped[str]  # UUID
    username: Mapped[str]  # owner
    title: Mapped[str]
    start_date: Mapped[date]
    end_date: Mapped[date]
    description: Mapped[str]
    created_at: Mapped[datetime]
```

**Activity Model**:
```python
class Activity(Base):
    __tablename__ = "activities"
    
    id: Mapped[str]  # UUID
    itinerary_id: Mapped[str]  # reference to itinerary
    username: Mapped[str]  # owner
    title: Mapped[str]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    location: Mapped[str]
    note: Mapped[str | None]
    created_at: Mapped[datetime]
```

**Features**:
- SQLAlchemy 2.0 style với `Mapped` types
- Automatic timestamp với `server_default=func.now()`
- Indexes trên username và foreign keys
- UUID primary keys cho itineraries & activities

#### **3. Repository Pattern**

**ItineraryRepo**:
```python
class ItineraryRepo:
    def __init__(self, session):
        self.session = session
    
    def create(self, username, payload):
        # Generate UUID
        # Create Itinerary instance
        # session.add() → session.commit() → session.refresh()
        # Return dict representation
    
    def list_by_user(self, username):
        # Query filter by username
        # Order by created_at desc
        # Return list of dicts
```

**ActivityRepo**:
```python
class ActivityRepo:
    def __init__(self, session):
        self.session = session
    
    def create(self, username, payload):
        # Generate UUID
        # Create Activity instance
        # session.add() → session.commit() → session.refresh()
        # Return dict representation
    
    def list_by_itinerary(self, username, itinerary_id):
        # Query filter by username AND itinerary_id
        # Order by created_at desc
        # Return list of dicts
```

**Benefits**:
- Separation of concerns (data access logic isolated)
- Testability (easy to mock repositories)
- Consistent return format (dicts with ISO date strings)
- UUID generation centralized

#### **4. API Schemas** (`schemas/`)

**ItineraryCreate**:
```python
class ItineraryCreate(BaseModel):
    title: str
    start_date: date
    end_date: date
    description: str
```

**ActivityCreate**:
```python
class ActivityCreate(BaseModel):
    itinerary_id: str
    title: str
    start_time: datetime
    end_time: datetime
    location: str
    note: str | None = None
```

**Validation**:
- Pydantic automatic validation
- Date/datetime parsing
- Required vs optional fields

#### **5. Dependencies** (`api/v1/dependencies.py`)

**JWT Authentication**:
```python
def get_current_user(credentials: HTTPAuthorizationCredentials):
    # Extract JWT token from Authorization header
    # Decode with SECRET_KEY
    # Return {"username": ...}
    # Raise 401 if invalid
```

**Database Session**:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Usage**:
```python
@router.post("/")
def create_itinerary(
    payload: ItineraryCreate,
    user=Depends(get_current_user),  # JWT auth
    db: Session = Depends(get_db),   # DB session
):
    ...
```

#### **6. Security** (`utils/security.py`)

**JWT Creation**:
```python
def create_access_token(data: dict):
    data["exp"] = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
```

**Password Handling**:
```python
def hash_password(password: str) -> str:
    return password  # ⚠️ NO HASHING - plain text!

def verify_password(password: str, stored_password: str) -> bool:
    return password == stored_password  # Plain comparison
```

**⚠️ CRITICAL SECURITY ISSUE**:
- Passwords NOT hashed
- JWT secret hardcoded
- **NOT production ready!**

### Đặc Điểm Thiết Kế

✅ **Repository Pattern**: Clean data access layer  
✅ **SQLAlchemy ORM**: Type-safe database operations  
✅ **Dependency Injection**: FastAPI Depends pattern  
✅ **UUID Primary Keys**: Unique identifiers  
✅ **Shared Database**: Same DB với middleware-service  
✅ **Transaction Support**: Automatic commit/rollback  
⚠️ **Security Issues**: Plain text passwords, hardcoded secrets  
⚠️ **No Relationships**: No SQLAlchemy foreign key constraints  
⚠️ **No Validation**: No business rule validation (date ranges, time conflicts)

---

## 🔌 API Endpoints

Service expose các endpoints qua prefix `/api/v1`:

### **1. Authentication Endpoints** (Public)

#### **Register**

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "message": "registered"
}
```

**Errors**:
- `400`: User exists

#### **Login**

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors**:
- `401`: Invalid credentials

**Token Usage**:
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/...
```

### **2. Itinerary Endpoints** (Protected)

#### **Create Itinerary**

```http
POST /api/v1/itineraries/
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "Trip to Paris",
  "start_date": "2025-03-01",
  "end_date": "2025-03-07",
  "description": "Spring vacation in Paris"
}
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user": "john_doe",
  "title": "Trip to Paris",
  "start_date": "2025-03-01",
  "end_date": "2025-03-07",
  "description": "Spring vacation in Paris"
}
```

**Fields**:
- `title` (required): Itinerary title
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `description` (required): Trip description

#### **List Itineraries**

```http
GET /api/v1/itineraries/
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user": "john_doe",
    "title": "Trip to Paris",
    "start_date": "2025-03-01",
    "end_date": "2025-03-07",
    "description": "Spring vacation in Paris"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "user": "john_doe",
    "title": "Weekend in Bangkok",
    "start_date": "2025-04-15",
    "end_date": "2025-04-17",
    "description": "Short getaway"
  }
]
```

**Note**: Only returns itineraries owned by authenticated user, ordered by created_at descending.

### **3. Activity Endpoints** (Protected)

#### **Create Activity**

```http
POST /api/v1/activities/
Content-Type: application/json
Authorization: Bearer <token>

{
  "itinerary_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Visit Eiffel Tower",
  "start_time": "2025-03-02T10:00:00",
  "end_time": "2025-03-02T12:00:00",
  "location": "Eiffel Tower, Paris",
  "note": "Buy tickets online in advance"
}
```

**Response:** `200 OK`
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "user": "john_doe",
  "itinerary_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Visit Eiffel Tower",
  "start_time": "2025-03-02T10:00:00",
  "end_time": "2025-03-02T12:00:00",
  "location": "Eiffel Tower, Paris",
  "note": "Buy tickets online in advance"
}
```

**Fields**:
- `itinerary_id` (required): Parent itinerary UUID
- `title` (required): Activity title
- `start_time` (required): Start datetime (ISO 8601)
- `end_time` (required): End datetime (ISO 8601)
- `location` (required): Activity location
- `note` (optional): Additional notes

#### **List Activities**

```http
GET /api/v1/activities/{itinerary_id}
Authorization: Bearer <token>
```

**Example**: `GET /api/v1/activities/550e8400-e29b-41d4-a716-446655440000`

**Response:** `200 OK`
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "user": "john_doe",
    "itinerary_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Visit Eiffel Tower",
    "start_time": "2025-03-02T10:00:00",
    "end_time": "2025-03-02T12:00:00",
    "location": "Eiffel Tower, Paris",
    "note": "Buy tickets online in advance"
  },
  {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "user": "john_doe",
    "itinerary_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Louvre Museum",
    "start_time": "2025-03-03T14:00:00",
    "end_time": "2025-03-03T18:00:00",
    "location": "Louvre Museum, Paris",
    "note": null
  }
]
```

**Note**: Only returns activities owned by authenticated user for the specified itinerary, ordered by created_at descending.

### **4. Health Check** (Public)

```http
GET /health
```

**Response:** `200 OK`
```json
{
  "status": "ok",
  "service": "itinerary-service-json"
}
```

---

## ⚙️ Giải Thích Hoạt Động

### **Flow 1: User Registration & JWT Login**

```
Client Request
    ↓
POST /api/v1/auth/register
{username: "john", password: "pass123"}
    ↓
[auth.py:register()]
    │
    ├─→ Get DB session
    │   db: Session = Depends(get_db)
    │
    ├─→ Check if user exists
    │   repo = UserRepo(db)
    │   if repo.get("john"):
    │       raise HTTPException(400, "User exists")
    │
    ├─→ Hash password (⚠️ plain text!)
    │   hashed = hash_password("pass123")
    │   # Returns: "pass123" unchanged
    │
    ├─→ Create user
    │   repo.create("john", "pass123")
    │   ↓
    │   [user_repo.py:create()]
    │       user = User(username="john", password="pass123")
    │       session.add(user)
    │       session.commit()
    │       ↓
    │       INSERT INTO users (username, password) VALUES ('john', 'pass123')
    │
    └─→ Return success
        {"message": "registered"}

─────────────────────────────────────

POST /api/v1/auth/login
{username: "john", password: "pass123"}
    ↓
[auth.py:login()]
    │
    ├─→ Get user from DB
    │   repo = UserRepo(db)
    │   user = repo.get("john")
    │   ↓
    │   SELECT * FROM users WHERE username = 'john'
    │   Returns: {"username": "john", "password": "pass123"}
    │
    ├─→ Verify password
    │   if not verify_password("pass123", "pass123"):
    │       # Plain text comparison
    │   Nếu sai → HTTPException(401, "Invalid credentials")
    │
    └─→ Create JWT token
        token = create_access_token({"sub": "john"})
        ↓
        [security.py:create_access_token()]
            data = {"sub": "john", "exp": datetime.utcnow() + timedelta(hours=1)}
            token = jwt.encode(data, "SECRET", algorithm="HS256")
            Returns: "eyJhbGci..."
        ↓
        Return {"access_token": "eyJhbGci..."}
```

**File liên quan:**
- `src/api/v1/endpoints/auth.py` (line 10-24)
- `src/infrastructure/user_repo.py`
- `src/utils/security.py` (line 9-22)

**Security Issues**:
1. ⚠️ Password plain text (no bcrypt/argon2)
2. ⚠️ JWT secret hardcoded
3. ⚠️ No password strength validation

### **Flow 2: Create Itinerary with JWT Auth**

```
POST /api/v1/itineraries/
Authorization: Bearer eyJhbGci...
{
  title: "Trip to Paris",
  start_date: "2025-03-01",
  end_date: "2025-03-07",
  description: "Spring vacation"
}
    ↓
[itineraries.py:create_itinerary()]
    │
    ├─→ JWT Authentication
    │   user = Depends(get_current_user)
    │   ↓
    │   [dependencies.py:get_current_user()]
    │       credentials = HTTPBearer extracts token
    │       payload = jwt.decode("eyJhbGci...", "SECRET", ["HS256"])
    │       if JWTError → HTTPException(401, "Invalid token")
    │       return {"username": "john"}
    │
    ├─→ Get DB session
    │   db = Depends(get_db)
    │   ↓
    │   [dependencies.py:get_db()]
    │       db = SessionLocal()
    │       yield db
    │       db.close()
    │
    ├─→ Pydantic validation
    │   payload: ItineraryCreate validated
    │   - title: str
    │   - start_date: date (parsed from "2025-03-01")
    │   - end_date: date
    │   - description: str
    │
    └─→ Create itinerary
        repo = ItineraryRepo(db)
        result = repo.create(user["username"], payload)
        ↓
    [itinerary_repo.py:create()]
        │
        ├─→ Generate UUID
        │   id = str(uuid.uuid4())
        │   # "550e8400-e29b-41d4-a716-446655440000"
        │
        ├─→ Create ORM instance
        │   item = Itinerary(
        │       id=id,
        │       username="john",
        │       title="Trip to Paris",
        │       start_date=date(2025, 3, 1),
        │       end_date=date(2025, 3, 7),
        │       description="Spring vacation"
        │   )
        │
        ├─→ Save to database
        │   session.add(item)
        │   session.commit()
        │   ↓
        │   INSERT INTO itineraries (id, username, title, start_date, end_date, description)
        │   VALUES ('550e...', 'john', 'Trip to Paris', '2025-03-01', '2025-03-07', '...')
        │
        ├─→ Refresh to get server defaults
        │   session.refresh(item)
        │   # Gets created_at from database
        │
        └─→ Return dict representation
            {
              "id": "550e...",
              "user": "john",
              "title": "Trip to Paris",
              "start_date": "2025-03-01",
              "end_date": "2025-03-07",
              "description": "Spring vacation"
            }
```

**File liên quan:**
- `src/api/v1/endpoints/itineraries.py` (line 10-17)
- `src/api/v1/dependencies.py` (line 12-19, 22-27)
- `src/infrastructure/itinerary_repo.py` (line 8-29)
- `src/infrastructure/database/models.py` (line 22-33)

**Key Points**:
1. **JWT Auth first**: User verified before any database operations
2. **UUID Generation**: Unique IDs generated in repository
3. **ORM Pattern**: SQLAlchemy handles SQL generation
4. **Transaction**: Auto-commit ensures data consistency

### **Flow 3: List Itineraries with Filtering**

```
GET /api/v1/itineraries/
Authorization: Bearer eyJhbGci...
    ↓
[itineraries.py:list_itineraries()]
    │
    ├─→ JWT Auth
    │   user = Depends(get_current_user)
    │   Returns: {"username": "john"}
    │
    ├─→ Get DB session
    │   db = Depends(get_db)
    │
    └─→ Query user's itineraries
        repo = ItineraryRepo(db)
        results = repo.list_by_user(user["username"])
        ↓
    [itinerary_repo.py:list_by_user()]
        │
        ├─→ Build query
        │   rows = session.query(Itinerary)\
        │       .filter(Itinerary.username == "john")\
        │       .order_by(Itinerary.created_at.desc())\
        │       .all()
        │   ↓
        │   SELECT * FROM itineraries 
        │   WHERE username = 'john' 
        │   ORDER BY created_at DESC
        │
        └─→ Convert to dicts
            [
              {
                "id": "550e...",
                "user": "john",
                "title": "Trip to Paris",
                "start_date": "2025-03-01",
                "end_date": "2025-03-07",
                "description": "..."
              },
              ...
            ]
```

**File liên quan:**
- `src/api/v1/endpoints/itineraries.py` (line 20-23)
- `src/infrastructure/itinerary_repo.py` (line 31-50)

**Security**: User isolation - chỉ thấy itineraries của mình

### **Flow 4: Create & List Activities**

```
POST /api/v1/activities/
Authorization: Bearer eyJhbGci...
{
  itinerary_id: "550e...",
  title: "Visit Eiffel Tower",
  start_time: "2025-03-02T10:00:00",
  end_time: "2025-03-02T12:00:00",
  location: "Eiffel Tower, Paris",
  note: "Buy tickets online"
}
    ↓
[activities.py:create_activity()]
    │
    ├─→ JWT Auth → user = {"username": "john"}
    │
    ├─→ Pydantic validation
    │   payload: ActivityCreate
    │   - itinerary_id: str (UUID)
    │   - start_time: datetime (parsed from ISO 8601)
    │   - end_time: datetime
    │
    └─→ Create activity
        repo = ActivityRepo(db)
        result = repo.create(user["username"], payload)
        ↓
    [activity_repo.py:create()]
        │
        ├─→ Generate UUID
        │   id = str(uuid.uuid4())
        │
        ├─→ Create ORM instance
        │   item = Activity(
        │       id=id,
        │       itinerary_id="550e...",
        │       username="john",
        │       title="Visit Eiffel Tower",
        │       start_time=datetime(2025, 3, 2, 10, 0),
        │       end_time=datetime(2025, 3, 2, 12, 0),
        │       location="Eiffel Tower, Paris",
        │       note="Buy tickets online"
        │   )
        │
        ├─→ Save to database
        │   session.add(item)
        │   session.commit()
        │   ↓
        │   INSERT INTO activities (id, itinerary_id, username, title, ...)
        │   VALUES ('770e...', '550e...', 'john', 'Visit Eiffel Tower', ...)
        │
        └─→ Return dict with ISO datetime strings

─────────────────────────────────────

GET /api/v1/activities/550e...
Authorization: Bearer eyJhbGci...
    ↓
[activities.py:list_activities()]
    │
    ├─→ JWT Auth → user = {"username": "john"}
    │
    └─→ Query activities
        repo = ActivityRepo(db)
        results = repo.list_by_itinerary(user["username"], "550e...")
        ↓
    [activity_repo.py:list_by_itinerary()]
        │
        ├─→ Build query with 2 filters
        │   rows = session.query(Activity)\
        │       .filter(
        │           Activity.username == "john",
        │           Activity.itinerary_id == "550e..."
        │       )\
        │       .order_by(Activity.created_at.desc())\
        │       .all()
        │   ↓
        │   SELECT * FROM activities 
        │   WHERE username = 'john' AND itinerary_id = '550e...'
        │   ORDER BY created_at DESC
        │
        └─→ Convert to dicts
            [
              {
                "id": "770e...",
                "itinerary_id": "550e...",
                "title": "Visit Eiffel Tower",
                "start_time": "2025-03-02T10:00:00",
                ...
              }
            ]
```

**File liên quan:**
- `src/api/v1/endpoints/activities.py` (line 10-25)
- `src/infrastructure/activity_repo.py` (line 8-56)

**Security**: Double filter (username AND itinerary_id) ensures user can only access their own activities

---

## 🚀 Cấu Hình và Triển Khai

### **1. Environment Variables**

Tạo file `.env` từ template:

```bash
cp .env.example .env
```

Cấu hình trong `.env`:

```bash
APP_NAME=itinerary-service
ENVIRONMENT=local
LOG_LEVEL=INFO

# PostgreSQL database (shared with middleware-service)
DATABASE_URL=postgresql+psycopg2://trip:trip@postgres:5432/trip_hub
```

### **2. Chạy Local (Development)**

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Đảm bảo PostgreSQL đang chạy
# Database: trip_hub, User: trip, Password: trip

# Chạy với uvicorn
uvicorn src.main:app --reload --port 8000

# Hoặc chạy trực tiếp
cd src
python main.py
```

**Database Setup**:
```sql
-- Tạo database (nếu chưa có)
CREATE DATABASE trip_hub;
CREATE USER trip WITH PASSWORD 'trip';
GRANT ALL PRIVILEGES ON DATABASE trip_hub TO trip;
```

### **3. Chạy với Docker**

Service được tích hợp trong docker-compose của hệ thống:

```bash
# Từ thư mục gốc của trip-hub
docker compose up -d --build

# Kiểm tra itinerary service
curl http://localhost:8000/health

# Response: {"status": "ok", "service": "itinerary-service-json"}
```

### **4. Test API Examples**

#### **Complete Workflow**

```bash
# 1. Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "traveler1", "password": "pass123"}'

# 2. Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "traveler1", "password": "pass123"}' \
  | jq -r '.access_token')

# 3. Create itinerary
ITINERARY_ID=$(curl -X POST http://localhost:8000/api/v1/itineraries/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Paris Adventure",
    "start_date": "2025-06-01",
    "end_date": "2025-06-07",
    "description": "Summer trip to Paris"
  }' | jq -r '.id')

# 4. List itineraries
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/itineraries/

# 5. Create activity
curl -X POST http://localhost:8000/api/v1/activities/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"itinerary_id\": \"$ITINERARY_ID\",
    \"title\": \"Eiffel Tower Visit\",
    \"start_time\": \"2025-06-02T10:00:00\",
    \"end_time\": \"2025-06-02T12:00:00\",
    \"location\": \"Eiffel Tower\",
    \"note\": \"Book tickets in advance\"
  }"

# 6. List activities
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/activities/$ITINERARY_ID"
```

---

## 📚 Dependencies

### Production (`requirements.txt`)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
```

**Key Libraries**:
- `fastapi`: Web framework
- `sqlalchemy`: ORM for PostgreSQL
- `psycopg2-binary`: PostgreSQL driver
- `python-jose`: JWT handling
- `pydantic-settings`: Configuration management

---

## 🔍 Troubleshooting

### **Lỗi: Database connection refused**

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Nguyên nhân**: PostgreSQL không chạy hoặc connection string sai

**Giải pháp**:
- Verify PostgreSQL đang chạy: `docker compose ps postgres`
- Check DATABASE_URL trong `.env`
- Ensure database `trip_hub` tồn tại

### **Lỗi: Invalid token (401)**

```json
{
  "detail": "Invalid token"
}
```

**Nguyên nhân**: JWT token invalid hoặc expired

**Giải pháp**:
- Token expires sau 1 hour - login lại để lấy token mới
- Verify token format: `Authorization: Bearer <token>`
- Check SECRET_KEY khớp giữa register và login

### **Lỗi: User exists (400)**

```json
{
  "detail": "User exists"
}
```

**Nguyên nhân**: Username đã được register

**Giải pháp**: Sử dụng username khác hoặc login với username hiện tại

### **Lỗi: Tables not created**

**Nguyên nhân**: `init_db()` chưa được gọi hoặc database permissions

**Giải pháp**:
```python
# Run manually
from src.infrastructure.database.connection import init_db
init_db()
```

Hoặc restart service (startup event sẽ tạo tables)

---

## 📝 Notes

### **Database Schema**

**Shared Tables**:
- `users` - Shared với middleware-service (same database)

**Service-Specific Tables**:
- `itineraries` - Travel itineraries
- `activities` - Activities within itineraries

**No Foreign Keys**:
- Không có SQLAlchemy relationships
- Không có database-level foreign key constraints
- Reference integrity được handle trong application code

### **Security Warnings** ⚠️

1. **Plain Text Passwords**:
   - `hash_password()` does NOT hash - returns plain text
   - **CRITICAL**: Implement bcrypt/argon2 hashing

2. **Hardcoded JWT Secret**:
   - `SECRET_KEY = "SECRET"` hardcoded
   - **CRITICAL**: Move to environment variables

3. **No Password Validation**:
   - No minimum length, complexity requirements
   - Vulnerable to weak passwords

### **Design Decisions**

- **Repository Pattern**: Clean separation of data access
- **UUID Primary Keys**: Globally unique identifiers
- **ISO Date/Time Strings**: Standard format in responses
- **User Ownership**: All data filtered by username
- **No Cascading Deletes**: Manual cleanup required
- **No Update/Delete Endpoints**: Read & Create only

### **Limitations**

- ❌ No itinerary update/delete endpoints
- ❌ No activity update/delete endpoints
- ❌ No validation of date ranges (end_date > start_date)
- ❌ No validation of activity times within itinerary dates
- ❌ No conflict detection (overlapping activities)
- ❌ No pagination for list endpoints
- ❌ No search/filter capabilities
- ❌ No soft deletes or audit trails

---

## 🎯 Future Improvements

### **1. Security Enhancements**

```python
# Implement proper password hashing
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

### **2. CRUD Operations**

```python
# Add update endpoint
@router.put("/itineraries/{itinerary_id}")
def update_itinerary(itinerary_id: str, payload: ItineraryUpdate, ...):
    repo.update(user["username"], itinerary_id, payload)

# Add delete endpoint
@router.delete("/itineraries/{itinerary_id}")
def delete_itinerary(itinerary_id: str, ...):
    repo.delete(user["username"], itinerary_id)
```

### **3. Business Logic Validation**

```python
# Validate date ranges
def validate_itinerary(payload: ItineraryCreate):
    if payload.end_date <= payload.start_date:
        raise HTTPException(400, "End date must be after start date")
    if payload.start_date < date.today():
        raise HTTPException(400, "Start date cannot be in the past")

# Validate activity times
def validate_activity(payload: ActivityCreate, itinerary: Itinerary):
    if payload.end_time <= payload.start_time:
        raise HTTPException(400, "End time must be after start time")
    if payload.start_time.date() < itinerary.start_date:
        raise HTTPException(400, "Activity starts before itinerary")
```

### **4. SQLAlchemy Relationships**

```python
class Itinerary(Base):
    ...
    activities = relationship("Activity", back_populates="itinerary")

class Activity(Base):
    ...
    itinerary = relationship("Itinerary", back_populates="activities")
    
    itinerary_id = mapped_column(
        String(36), 
        ForeignKey("itineraries.id", ondelete="CASCADE")
    )
```

### **5. Pagination**

```python
@router.get("/itineraries/")
def list_itineraries(
    skip: int = 0,
    limit: int = 10,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return repo.list_by_user(user["username"], skip=skip, limit=limit)
```

### **6. Search & Filtering**

```python
@router.get("/itineraries/search")
def search_itineraries(
    q: str = None,  # Search query
    start_after: date = None,  # Filter by start date
    sort_by: str = "created_at",
    ...
):
    return repo.search(user["username"], q, start_after, sort_by)
```

### **7. Conflict Detection**

```python
def check_activity_conflicts(
    username: str,
    itinerary_id: str,
    start_time: datetime,
    end_time: datetime
) -> list:
    # Find overlapping activities
    conflicts = session.query(Activity).filter(
        Activity.username == username,
        Activity.itinerary_id == itinerary_id,
        or_(
            and_(Activity.start_time <= start_time, Activity.end_time > start_time),
            and_(Activity.start_time < end_time, Activity.end_time >= end_time)
        )
    ).all()
    return conflicts
```

---

## 📐 Tích Hợp với Middleware

Service được truy cập qua Middleware Service (API Gateway):

```
Client
  ↓
Middleware Service (Port 9000) - JWT Auth
  ↓
Itinerary Service (Port 8000) - Internal
  ↓
PostgreSQL Database (Port 5432)
```

**Proxy Routes via Middleware**:
```bash
# Thay vì gọi trực tiếp
POST http://itinerary-service:8000/api/v1/itineraries/

# Client gọi qua middleware
POST http://localhost:9000/api/v1/itinerary/itineraries
Authorization: Bearer <JWT_TOKEN>
```

**Shared Database**:
- `users` table được share giữa middleware-service và itinerary-service
- Same PostgreSQL database: `trip_hub`
- User registration có thể xảy ra ở either service
- JWT tokens issued by either service đều valid

---

## 🚀 Quick Start

```bash
# 1. Start PostgreSQL
docker compose up -d postgres

# 2. Run service
uvicorn src.main:app --reload --port 8000

# 3. Register & Login
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "pass123"}'

TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "pass123"}' \
  | jq -r '.access_token')

# 4. Create trip plan
curl -X POST http://localhost:8000/api/v1/itineraries/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Summer Vacation",
    "start_date": "2025-07-01",
    "end_date": "2025-07-14",
    "description": "Two weeks in Europe"
  }'
```

---

**Service Status**: ✅ Functional (Development)  
**Security Status**: ⚠️ **NOT Production Ready** (plain text passwords)  
**Last Updated**: December 2024  
**Maintainer**: Trip Hub Team
