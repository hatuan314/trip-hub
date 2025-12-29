# Middleware Service (API Gateway)

**API Gateway** cho toàn bộ hệ thống Trip Hub microservices. Service này đóng vai trò là single entry point tại `http://localhost:9000`, cung cấp JWT authentication, request routing và proxy tất cả requests đến các downstream services.

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

### 1. **API Gateway cho Toàn Hệ Thống**
- Single entry point tại `http://localhost:9000` cho tất cả client requests
- Là lớp trung gian giữa client (Web UI) và các microservices backend
- Không client nào truy cập trực tiếp vào các internal services
- Expose port 9000 ra public, các services khác chỉ accessible trong Docker network

### 2. **JWT Authentication & Authorization**
- Cung cấp user registration và login endpoints
- Lưu user credentials trong PostgreSQL database local
- Phát hành JWT token khi login thành công (expiry: 1 hour)
- Bảo vệ tất cả proxy endpoints bằng JWT dependency `get_current_user`
- Chỉ auth endpoints (`/register`, `/login`) và `/health` là public

### 3. **Request Proxying & Routing**
- Proxy tất cả HTTP methods (GET, POST, PUT, PATCH, DELETE, OPTIONS) đến downstream services
- Pattern: `/api/v1/{service}/{path...}` 
- Services được hỗ trợ: `destination`, `weather`, `itinerary`, `booking`
- Giữ nguyên request body, query parameters, headers khi forward
- Tự động rewrite `Location` headers để maintain API Gateway abstraction

### 4. **Wrapper Routes (Convenience Endpoints)**
- Cung cấp friendly routes với explicit OpenAPI documentation
- Ví dụ: `/api/v1/destination/destinations`, `/api/v1/weather/current`
- Internally gọi đến generic proxy mechanism
- Tốt hơn cho developer experience và API documentation

### 5. **Service Discovery & Health Monitoring**
- `ServiceRouter` quản lý map giữa service names và base URLs
- Health check endpoint hiển thị danh sách services đang được cấu hình
- Dễ dàng thêm/xóa services qua configuration

### 6. **Error Handling**
- Timeout errors (504 Gateway Timeout) khi downstream service không phản hồi
- Upstream errors (502 Bad Gateway) khi có lỗi từ downstream services
- Authentication errors (401 Unauthorized) cho invalid JWT tokens
- Service not found (404) cho unknown service names

### 7. **CORS Support**
- Cho phép Web UI (localhost:8080) gọi API
- Allow credentials, all methods, all headers
- Hỗ trợ cross-origin requests

---

## 🏗️ Thiết Kế Phần Mềm

Service được thiết kế theo **API Gateway Pattern** với kiến trúc rõ ràng:

```
src/
├── main.py                          # Entry point, FastAPI app + CORS
├── config/
│   └── settings.py                  # Configuration (service URLs, timeouts)
├── api/
│   └── v1/
│       ├── router.py                # Router aggregation
│       ├── dependencies.py          # JWT authentication dependency
│       └── endpoints/
│           ├── auth.py              # Register/Login endpoints
│           ├── proxy.py             # Generic proxy endpoints (all methods)
│           └── wrappers.py          # Convenience wrapper endpoints
├── core/
│   ├── bootstrap.py                 # Service registry initialization
│   └── service_router.py            # Service discovery & URL building
├── infrastructure/
│   ├── database/
│   │   ├── connection.py            # SQLAlchemy engine & session
│   │   └── models.py                # User model
│   └── user_repo.py                 # User repository
├── schemas/
│   └── auth.py                      # Pydantic schemas (UserRegister, UserLogin)
└── utils/
    ├── security.py                  # JWT creation, password hashing
    └── auth_sync_client.py          # Sync user to other services
```

### Kiến Trúc Chi Tiết

#### **1. Main Application** (`main.py`)

**Khởi tạo**:
```python
app = FastAPI(title="Middleware Service", version="0.1.0")
```

**CORS Middleware**:
- Cho phép origins: `http://localhost:8080`, `http://127.0.0.1:8080`
- Allow credentials: True
- Allow all methods và headers

**Startup Event**:
- Gọi `init_db()` để tạo tables trong PostgreSQL
- Khởi tạo User table nếu chưa tồn tại

**Health Check**:
```python
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "middleware-service",
        "forwarding_to": ["booking", "destination", "itinerary", "weather"]
    }
```

#### **2. Service Router** (`core/service_router.py`)

**Responsibility**: Map service names to downstream URLs và build target URLs.

**Constructor**:
```python
ServiceRouter(service_map: Mapping[str, str], api_prefix: str)
```

**Key Methods**:

- `build_target(service_name, path)`: Build full target URL
  - Pattern: `{base_url}{api_prefix}/{path}`
  - Special case: `/health` không thêm api_prefix
  - Returns `None` nếu service không tồn tại

- `available_services()`: Returns sorted list of service names

- `get_base_url(service_name)`: Get base URL of a service

**Bootstrap** (`core/bootstrap.py`):
```python
service_router = ServiceRouter({
    "destination": settings.destination_service_url,
    "weather": settings.weather_service_url,
    "itinerary": settings.itinerary_service_url,
    "booking": settings.booking_service_url,
}, api_prefix=settings.api_prefix)
```

#### **3. Authentication System**

**JWT Strategy**:
- Algorithm: HS256 (HMAC with SHA-256)
- Secret: "SECRET" (hardcoded - **not production ready**)
- Expiry: 1 hour
- Token format: `{"sub": username, "exp": timestamp}`

**User Storage**:
- PostgreSQL database (shared with itinerary-service)
- Table: `users` (id, username, password, created_at)
- **Security Issue**: Passwords stored in **plain text** (not hashed!)

**Dependencies** (`dependencies.py`):
```python
def get_current_user(credentials: HTTPAuthorizationCredentials):
    # Decode JWT token
    # Raise 401 if invalid
    return {"username": payload.get("sub")}
```

Used in all protected endpoints: `user=Depends(get_current_user)`

#### **4. Proxy Mechanism** (`endpoints/proxy.py`)

**Generic Proxy Function**:
```python
async def proxy_request(service: str, request: Request, path: str = "")
```

**Flow**:
1. Build target URL via `service_router.build_target()`
2. Extract headers, body, query params from incoming request
3. Forward request với `httpx.AsyncClient`:
   - Timeout: configurable (default 10s)
   - Preserve method, body, params, headers
4. Handle errors:
   - `TimeoutException` → 504 Gateway Timeout
   - `HTTPError` → 502 Bad Gateway
5. Rewrite `Location` header nếu redirect từ downstream service
6. Return response với same status code, headers, body

**Supported Methods**:
- GET, POST, PUT, PATCH, DELETE, OPTIONS
- Both `/{service}` và `/{service}/{path:path}` patterns

#### **5. Wrapper Endpoints** (`endpoints/wrappers.py`)

**Purpose**: Cung cấp explicit, documented endpoints thay vì generic proxy.

**Examples**:
```python
@router.get("/destination/destinations")
async def destination_search(query: str, country: str | None, ...):
    return await proxy_request(service="destination", path="destinations", ...)

@router.get("/weather/current")
async def weather_current(location: str, ...):
    return await proxy_request(service="weather", path="weather/current", ...)
```

**Benefits**:
- Better OpenAPI/Swagger documentation
- Type hints for query parameters
- Easier to understand API structure
- Client code generation friendly

#### **6. Database & Repository**

**Connection** (`database/connection.py`):
```python
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)
```

**User Model** (`database/models.py`):
```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

**User Repository** (`user_repo.py`):
```python
class UserRepo:
    def create(username, password) -> dict
    def get(username) -> dict | None
```

### Đặc Điểm Thiết Kế

✅ **Single Entry Point**: Tất cả traffic đi qua một gateway  
✅ **Authentication Centralization**: JWT auth ở API Gateway, không cần implement ở mỗi service  
✅ **Service Abstraction**: Clients không biết về internal service topology  
✅ **Flexible Routing**: Dễ dàng thêm/xóa/sửa services  
✅ **Error Handling**: Consistent error responses  
⚠️ **Security Warning**: Plain text passwords - **NOT production ready**  
⚠️ **Hardcoded Secret**: JWT secret should be in env vars  

---

## 🔌 API Endpoints

Service expose các endpoints sau qua prefix `/api/v1`:

### **1. Health Check** (Public)

```http
GET /health
```

**Response:** `200 OK`
```json
{
  "status": "ok",
  "service": "middleware-service",
  "forwarding_to": ["booking", "destination", "itinerary", "weather"]
}
```

### **2. Authentication Endpoints** (Public)

#### **Register**

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "user123",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "message": "registered"
}
```

**Errors:**
- `400`: User exists (local)

**Note**: Service cũng cố gắng sync user sang itinerary-service (port 8000), nhưng lỗi chỉ được log, không fail registration.

#### **Login**

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user123",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:**
- `401`: Invalid credentials

**Token Usage**:
```bash
curl -H "Authorization: Bearer <token>" http://localhost:9000/api/v1/...
```

### **3. Generic Proxy Endpoints** (Protected - Requires JWT)

#### **Pattern**:
```http
{METHOD} /api/v1/{service}/{path...}
```

**Supported Methods**: GET, POST, PUT, PATCH, DELETE, OPTIONS

**Services**: `destination`, `weather`, `itinerary`, `booking`

**Examples**:
```bash
# GET request
GET /api/v1/destination/destinations?query=paris
  → destination-service:8000/api/v1/destinations?query=paris

# POST request
POST /api/v1/booking/flights/search
  → booking-service:8000/api/v1/flights/search

# With path parameter
GET /api/v1/booking/flights/ABC123
  → booking-service:8000/api/v1/flights/ABC123
```

**Errors:**
- `401`: Invalid token / Missing Authorization header
- `404`: Unknown service '{service}'
- `502`: Error forwarding request to {service}
- `504`: Request to {service} timed out

### **4. Wrapper Endpoints** (Protected - Better Documentation)

#### **Destination Service**

```http
GET /api/v1/destination/destinations?query={keyword}&country={country_code}
GET /api/v1/destination/attractions?location={location}&radius_m={radius}&limit={limit}
GET /api/v1/destination/hotels?location={location}&radius_m={radius}&limit={limit}
```

#### **Weather Service**

```http
GET /api/v1/weather/current?location={location}
GET /api/v1/weather/forecast?location={location}
```

#### **Booking Service**

```http
GET /api/v1/booking/cities?keyword={keyword}&country_code={code}&limit={limit}
GET /api/v1/booking/cities/{iata_code}
POST /api/v1/booking/flights/search
GET /api/v1/booking/flights/{offer_id}
POST /api/v1/booking/hotels/search
POST /api/v1/booking/hotels/offers
GET /api/v1/booking/health
```

#### **Itinerary Service**

```http
POST /api/v1/itinerary/itineraries
GET /api/v1/itinerary/itineraries
POST /api/v1/itinerary/activities
GET /api/v1/itinerary/activities/{itinerary_id}
GET /api/v1/itinerary/health
```

---

## ⚙️ Giải Thích Hoạt Động

### **Flow 1: User Registration**

```
Client Request
    ↓
POST /api/v1/auth/register
{username: "john", password: "pass123"}
    ↓
[auth.py:register()]
    │
    ├─→ Khởi tạo UserRepo(db)
    │
    ├─→ Kiểm tra user đã tồn tại?
    │   repo.get("john")
    │   ↓
    │   Nếu tồn tại → HTTPException 400 "User exists (local)"
    │
    ├─→ Hash password (⚠️ thực tế KHÔNG hash - plain text!)
    │   hashed = hash_password("pass123")
    │   # Returns: "pass123" (no hashing!)
    │
    ├─→ Lưu vào PostgreSQL
    │   repo.create("john", "pass123")
    │   ↓
    │   [user_repo.py:create()]
    │       user = User(username="john", password="pass123")
    │       session.add(user)
    │       session.commit()
    │
    └─→ Sync sang itinerary-service (best-effort)
        try:
            await sync_register("john", "pass123")
            # POST http://itinerary-service:8000/api/v1/auth/register
        except Exception as e:
            print(f"[SYNC ERROR] {e}")
            # ⚠️ Không rollback, chỉ log error
        ↓
    Return {"message": "registered"}
```

**File liên quan:**
- `src/api/v1/endpoints/auth.py` (line 12-30)
- `src/infrastructure/user_repo.py` (line 5-12)
- `src/utils/security.py` (line 9-11)
- `src/utils/auth_sync_client.py`

**Security Issues**:
1. Password KHÔNG được hash - lưu plain text
2. Sync error không rollback transaction - có thể inconsistent state
3. JWT secret hardcoded

### **Flow 2: User Login & JWT Generation**

```
POST /api/v1/auth/login
{username: "john", password: "pass123"}
    ↓
[auth.py:login()]
    │
    ├─→ Khởi tạo UserRepo(db)
    │
    ├─→ Lấy user từ DB
    │   user = repo.get("john")
    │   ↓
    │   [user_repo.py:get()]
    │       SELECT * FROM users WHERE username = 'john'
    │       return {"username": "john", "password": "pass123"}
    │
    ├─→ Verify credentials
    │   if not user or not verify_password("pass123", user["password"]):
    │       ↓
    │       [security.py:verify_password()]
    │           return "pass123" == "pass123"  # Plain text comparison
    │       ↓
    │   Nếu sai → HTTPException 401 "Invalid credentials"
    │
    └─→ Tạo JWT token
        token = create_access_token({"sub": "john"})
        ↓
        [security.py:create_access_token()]
            data = {"sub": "john", "exp": datetime.utcnow() + timedelta(hours=1)}
            return jwt.encode(data, "SECRET", algorithm="HS256")
            # Returns: "eyJhbGci..."
        ↓
    Return {"access_token": "eyJhbGci..."}
```

**File liên quan:**
- `src/api/v1/endpoints/auth.py` (line 33-40)
- `src/utils/security.py` (line 14-22)

**Token Structure**:
```json
{
  "sub": "john",
  "exp": 1735488000
}
```

### **Flow 3: Protected Request with JWT**

```
Client Request
    ↓
GET /api/v1/destination/destinations?query=paris
Authorization: Bearer eyJhbGci...
    ↓
[dependencies.py:get_current_user()] ← Dependency
    │
    ├─→ Extract token from Authorization header
    │   HTTPBearer security scheme
    │   credentials.credentials = "eyJhbGci..."
    │
    ├─→ Decode & validate JWT
    │   try:
    │       payload = jwt.decode(
    │           "eyJhbGci...",
    │           SECRET_KEY="SECRET",
    │           algorithms=["HS256"]
    │       )
    │       # payload = {"sub": "john", "exp": ...}
    │   except JWTError:
    │       raise HTTPException(401, "Invalid token")
    │
    └─→ Return user info
        return {"username": "john"}
        ↓
[wrappers.py:destination_search()] hoặc [proxy.py:proxy_get()]
    user = {"username": "john"}  # From dependency
    ↓
    Proceed with proxy logic...
```

**File liên quan:**
- `src/api/v1/dependencies.py` (line 12-20)

**Error Cases**:
- Missing `Authorization` header → 403 Forbidden (from HTTPBearer)
- Invalid JWT format → 401 "Invalid token"
- Expired token → 401 "Invalid token"
- Wrong secret/algorithm → 401 "Invalid token"

### **Flow 4: Generic Proxy Request**

```
GET /api/v1/destination/destinations?query=paris
Authorization: Bearer <valid-token>
    ↓
[proxy.py:proxy_get()] 
    service = "destination"
    path = "destinations"
    user = {"username": "john"}  # From JWT dependency
    ↓
    await proxy_request(service="destination", request=request, path="destinations")
        ↓
    [proxy.py:proxy_request()]
        │
        ├─→ Build target URL
        │   target_url = service_router.build_target("destination", "destinations")
        │   ↓
        │   [service_router.py:build_target()]
        │       base_url = routes["destination"]
        │                = "http://destination-service:8000"
        │       normalized_path = "destinations"
        │       return f"{base_url}{api_prefix}/{normalized_path}"
        │              = "http://destination-service:8000/api/v1/destinations"
        │   ↓
        │   if not target_url:
        │       raise HTTPException(404, "Unknown service 'destination'")
        │
        ├─→ Prepare request
        │   headers = {k: v for k, v in request.headers.items() if k != "host"}
        │   body = await request.body()
        │   # body = b"" (GET request)
        │
        ├─→ Forward request với httpx
        │   try:
        │       async with httpx.AsyncClient(timeout=10.0) as client:
        │           upstream_response = await client.request(
        │               method="GET",
        │               url="http://destination-service:8000/api/v1/destinations",
        │               content=b"",
        │               params={"query": "paris"},
        │               headers={...}
        │           )
        │   except httpx.TimeoutException:
        │       raise HTTPException(504, "Request to destination timed out")
        │   except httpx.HTTPError:
        │       raise HTTPException(502, "Error forwarding request")
        │
        ├─→ Process response headers
        │   filtered_headers = {
        │       k: v for k, v in upstream_response.headers.items()
        │       if k not in ["content-length", "transfer-encoding", ...]
        │   }
        │
        ├─→ Rewrite Location header (nếu có redirect)
        │   if "location" in filtered_headers:
        │       # Convert: http://destination-service:8000/api/v1/xxx
        │       # To: /api/v1/destination/xxx
        │       # (Maintain API Gateway abstraction)
        │
        └─→ Return response
            Response(
                content=upstream_response.content,
                status_code=upstream_response.status_code,
                headers=filtered_headers,
                media_type=upstream_response.headers["content-type"]
            )
```

**File liên quan:**
- `src/api/v1/endpoints/proxy.py` (line 20-22, 75-136)
- `src/core/service_router.py` (line 13-23)

**Key Features**:
1. **Preserves Everything**: method, body, query params, headers
2. **Error Translation**: httpx errors → HTTP status codes
3. **Location Rewriting**: Maintain gateway abstraction
4. **Timeout Handling**: Configurable timeout per request

### **Flow 5: Service Discovery & Routing**

```
[main.py] Startup
    ↓
Import service_router from bootstrap
    ↓
[bootstrap.py]
    service_router = ServiceRouter({
        "destination": "http://destination-service:8000",
        "weather": "http://weather-service:8000",
        "itinerary": "http://itinerary-service:8000",
        "booking": "http://booking-service:8000",
    }, api_prefix="/api/v1")
    ↓
[service_router.py:__init__()]
    self.api_prefix = "/api/v1"
    self.routes = {
        "destination": "http://destination-service:8000",
        "weather": "http://weather-service:8000",
        "itinerary": "http://itinerary-service:8000",
        "booking": "http://booking-service:8000"
    }
    ↓
Available for:
    - service_router.build_target(service, path)
    - service_router.available_services()
    - service_router.get_base_url(service)
```

**File liên quan:**
- `src/core/bootstrap.py` (line 5-13)
- `src/core/service_router.py` (line 4-30)
- `src/config/settings.py` (line 15-18)

**Configuration-Driven**:
- Service URLs từ environment variables
- Dễ dàng thêm/xóa services bằng cách update `bootstrap.py`
- Health check tự động list available services

---

## 🚀 Cấu Hình và Triển Khai

### **1. Environment Variables**

Tạo file `.env` từ template:

```bash
cp .env.example .env
```

Cấu hình trong `.env`:

```bash
APP_NAME=middleware-service
ENVIRONMENT=local
LOG_LEVEL=INFO
API_PREFIX=/api/v1
HTTP_TIMEOUT=10

# PostgreSQL database (shared with itinerary-service)
DATABASE_URL=postgresql+psycopg2://trip:trip@postgres:5432/trip_hub

# Downstream service URLs (Docker service names)
DESTINATION_SERVICE_URL=http://destination-service:8000
WEATHER_SERVICE_URL=http://weather-service:8000
ITINERARY_SERVICE_URL=http://itinerary-service:8000
BOOKING_SERVICE_URL=http://booking-service:8000
```

### **2. Chạy Local (Development)**

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Đảm bảo PostgreSQL đang chạy
# Database: trip_hub, User: trip, Password: trip

# Chạy với uvicorn
uvicorn src.main:app --reload --port 9000

# Truy cập Swagger docs
open http://localhost:9000/docs
```

**Note**: Khi chạy local, cần adjust service URLs trong `.env` nếu services chạy ở ports khác.

### **3. Chạy với Docker**

Service được tích hợp trong docker-compose của hệ thống:

```bash
# Từ thư mục gốc của trip-hub
docker compose up -d --build

# Kiểm tra middleware health
curl http://localhost:9000/health

# Response:
{
  "status": "ok",
  "service": "middleware-service",
  "forwarding_to": ["booking", "destination", "itinerary", "weather"]
}
```

### **4. Authentication Flow**

```bash
# 1. Register
curl -X POST http://localhost:9000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "pass123"}'

# Response: {"message": "registered"}

# 2. Login
curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "pass123"}'

# Response: {"access_token": "eyJhbGci..."}

# 3. Use token in subsequent requests
TOKEN="eyJhbGci..."
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/destination/destinations?query=paris"
```

### **5. Proxy Examples**

```bash
# Destination service
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/destination/destinations?query=tokyo"

# Weather service
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/weather/current?location=Paris"

# Booking service - flight search
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "http://localhost:9000/api/v1/booking/flights/search" \
  -d '{
    "origin": "PAR",
    "destination": "NYC",
    "departure_date": "2024-06-01",
    "adults": 1
  }'

# Itinerary service
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/itinerary/itineraries"
```

### **6. API Documentation**

Khi service đang chạy:

- **Swagger UI**: http://localhost:9000/docs
- **ReDoc**: http://localhost:9000/redoc

Swagger UI cho phép:
- Test API endpoints directly
- View request/response schemas
- Authenticate với JWT token (click "Authorize" button)

---

## 📚 Dependencies

### Production (`requirements.txt`)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
httpx==0.25.2
python-jose[cryptography]==3.3.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
```

**Key Libraries**:
- `fastapi`: Web framework
- `httpx`: Async HTTP client for proxying
- `python-jose`: JWT encoding/decoding
- `sqlalchemy`: ORM for PostgreSQL
- `psycopg2-binary`: PostgreSQL driver

---

## 🔍 Troubleshooting

### **Lỗi: Invalid token (401)**

```json
{
  "detail": "Invalid token"
}
```

**Nguyên nhân**: JWT token invalid, expired, hoặc missing

**Giải pháp**:
- Đảm bảo include header: `Authorization: Bearer <token>`
- Token có thể đã expire (1 hour) - login lại để lấy token mới
- Verify token format là `Bearer eyJ...`

### **Lỗi: Unknown service (404)**

```json
{
  "detail": "Unknown service 'xyz'"
}
```

**Nguyên nhân**: Service name không tồn tại trong service registry

**Valid services**: `destination`, `weather`, `itinerary`, `booking`

### **Lỗi: Request timed out (504)**

```json
{
  "detail": "Request to destination timed out"
}
```

**Nguyên nhân**: Downstream service không phản hồi trong timeout (10s)

**Giải pháp**:
- Kiểm tra downstream service có đang chạy không: `docker compose ps`
- Xem logs: `docker compose logs destination-service`
- Tăng timeout trong `.env`: `HTTP_TIMEOUT=30`

### **Lỗi: Error forwarding request (502)**

```json
{
  "detail": "Error forwarding request to weather"
}
```

**Nguyên nhân**: Lỗi khi gọi downstream service (connection refused, network error)

**Giải pháp**:
- Verify service URLs trong `.env` đúng
- Check Docker network: `docker network inspect trip-network`
- Verify services trong cùng network

### **Lỗi: User exists (400)**

```json
{
  "detail": "User exists (local)"
}
```

**Nguyên nhân**: Username đã được đăng ký

**Giải pháp**: Sử dụng username khác

### **Lỗi: Invalid credentials (401)**

**Nguyên nhân**: Username hoặc password sai khi login

**Giải pháp**: Kiểm tra lại credentials

---

## 📐 Kiến Trúc Tích Hợp

```
┌─────────────────────────────────────────────────────────┐
│                    Web UI (Port 8080)                   │
│                  (HTML/CSS/JavaScript)                  │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP Requests (JWT Token)
                      ↓
┌─────────────────────────────────────────────────────────┐
│         Middleware Service (Port 9000) - PUBLIC         │
│              ┌────────────────────────────┐             │
│              │  API Gateway Functions:    │             │
│              │  • JWT Authentication      │             │
│              │  • Request Routing         │             │
│              │  • Request Proxying        │             │
│              │  • CORS Handling          │             │
│              │  • Error Translation       │             │
│              └────────────────────────────┘             │
└──┬──────────────┬──────────────┬──────────────┬─────────┘
   │              │              │              │
   │ Docker       │ Docker       │ Docker       │ Docker
   │ Network      │ Network      │ Network      │ Network
   │              │              │              │
   ↓              ↓              ↓              ↓
┌─────────┐  ┌─────────┐  ┌──────────┐  ┌─────────┐
│Destination│ │ Weather │ │Itinerary │ │ Booking │
│  :8000    │ │  :8000  │ │  :8000   │ │  :8000  │
│(INTERNAL) │ │(INTERNAL)│ │(INTERNAL)│ │(INTERNAL)│
└─────────┘  └────┬────┘  └────┬─────┘  └────┬────┘
                  │            │             │
              ┌───┴───┐    ┌───┴───┐    ┌───┴───┐
              │Postgres│    │Postgres│   │ Redis │
              │  :5432 │    │  :5432 │   │ :6379 │
              └────────┘    └────────┘   └───────┘
```

**Vai trò**: 
- **Single Entry Point** cho tất cả external requests
- **Authentication & Authorization** centralization
- **Service Abstraction** - clients không biết về internal topology
- **Request Routing** based on service name
- **Error Handling** và translation

---

## 📝 Notes

### **Security Warnings** ⚠️

1. **Plain Text Passwords**: 
   - `hash_password()` không thực sự hash - trả về plain text
   - **CRITICAL**: Phải implement proper password hashing (bcrypt, argon2)

2. **Hardcoded JWT Secret**:
   - `SECRET_KEY = "SECRET"` hardcoded trong code
   - **CRITICAL**: Move to environment variables

3. **No HTTPS**:
   - Production cần HTTPS/TLS termination

4. **No Rate Limiting**:
   - Vulnerable to brute force attacks

### **Architecture Notes**

- **Stateless**: Middleware không lưu state, chỉ route requests
- **Database Shared**: PostgreSQL database được share với itinerary-service
- **Sync Issues**: User registration sync sang itinerary-service có thể fail silently
- **Service Discovery**: Static configuration, không có dynamic service discovery
- **No Circuit Breaker**: Không có protection khi downstream services fail
- **No Retry Logic**: Failed requests không được retry

### **Performance Considerations**

- **Timeout**: Default 10s có thể quá ngắn cho slow operations
- **Connection Pooling**: httpx AsyncClient được tạo mới cho mỗi request (có thể optimize)
- **Database Connections**: SQLAlchemy session management cần optimize cho production

---

## 🎯 Future Improvements

1. **Security Enhancements**:
   - Implement proper password hashing (bcrypt)
   - Move JWT secret to environment variables
   - Add rate limiting middleware
   - Implement refresh tokens
   - Add API key authentication option

2. **Resilience**:
   - Circuit breaker pattern cho downstream services
   - Retry logic với exponential backoff
   - Health check cho downstream services
   - Fallback responses

3. **Observability**:
   - Structured logging
   - Request tracing (OpenTelemetry)
   - Metrics collection (Prometheus)
   - Performance monitoring

4. **Features**:
   - Dynamic service discovery (Consul, etcd)
   - Request/response caching
   - Request validation & transformation
   - Response aggregation (BFF pattern)
   - WebSocket support

5. **Developer Experience**:
   - Better error messages
   - Request/response logging
   - API versioning strategy
   - OpenAPI spec generation automation
