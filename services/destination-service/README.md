# Destination Service

Microservice quản lý thông tin điểm đến du lịch, tìm kiếm điểm tham quan và khách sạn sử dụng Geoapify API. Được xây dựng theo Clean Architecture với FastAPI.

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

### 1. **Tìm Kiếm Điểm Đến** 
- Tìm kiếm các điểm đến du lịch theo từ khóa (tên địa điểm, thành phố, quốc gia)
- Hỗ trợ lọc theo quốc gia cụ thể
- Trả về danh sách điểm đến với thông tin: `id`, `name`, `country`, `description`
- Loại bỏ các kết quả trùng lặp dựa trên `id`

### 2. **Lấy Chi Tiết Điểm Đến**
- Lấy thông tin chi tiết một điểm đến dựa trên chuỗi tìm kiếm
- Trả về một bản ghi `DestinationOut` hoặc lỗi 404 nếu không tìm thấy
- Lấy kết quả đầu tiên từ danh sách kết quả tìm kiếm

### 3. **Tìm Điểm Tham Quan**
- Tìm các điểm tham quan (attractions) gần một địa điểm cụ thể
- Quy trình: Geocode địa điểm → Gọi Places API với category `tourism`
- Trả về danh sách với thông tin: `id`, `destination_id`, `name`
- Tùy chỉnh bán kính tìm kiếm (mặc định 5000m) và giới hạn kết quả (mặc định 20)

### 4. **Tìm Khách Sạn**
- Tìm khách sạn gần một địa điểm cụ thể  
- Quy trình: Geocode địa điểm → Gọi Places API với category `accommodation.hotel`
- Trả về danh sách với thông tin: `id`, `destination_id`, `name`
- Tùy chỉnh bán kính tìm kiếm và giới hạn kết quả

### 5. **Yêu Cầu Bắt Buộc**
- Bắt buộc phải cấu hình `GEOAPIFY_API_KEY` trong file `.env`
- Thiếu API key sẽ trả về lỗi 500 Internal Server Error
- Không sử dụng database nội bộ, toàn bộ dữ liệu lấy từ Geoapify API

---

## 🏗️ Thiết Kế Phần Mềm

Service được thiết kế theo **Clean Architecture** với tách biệt rõ ràng các layer:

```
src/
├── main.py                          # Entry point, FastAPI app
├── config/
│   └── settings.py                  # Configuration management
├── api/
│   └── v1/
│       ├── router.py                # API router aggregation
│       └── endpoints/
│           ├── destinations.py      # Destinations endpoints
│           ├── attractions.py       # Attractions endpoints
│           ├── hotels.py            # Hotels endpoints
│           └── search.py            # Search endpoints
├── core/
│   ├── entities/                    # Domain entities (dataclasses)
│   │   ├── destination.py
│   │   ├── attraction.py
│   │   └── hotel.py
│   ├── interfaces/                  # Abstract interfaces
│   │   └── external_api_client.py
│   └── use_cases/                   # Business logic
│       ├── search_destinations.py
│       ├── get_destination_info.py
│       ├── get_attractions.py
│       └── get_nearby_hotels.py
├── infrastructure/
│   └── external/
│       └── geoapify_client.py       # Geoapify API client
└── schemas/                         # Pydantic schemas for API I/O
    ├── destination.py
    ├── attraction.py
    └── hotel.py
```

### Kiến Trúc Chi Tiết

#### **1. API Layer** (`api/v1/`)
- **Router** (`router.py`): Tổng hợp các endpoint groups
- **Endpoints**: Nhóm theo domain (destinations, attractions, hotels, search)
- Mỗi endpoint xử lý HTTP request/response và validation
- Gọi Use Cases để thực thi business logic

#### **2. Core Layer** (`core/`)

**Entities** (Domain models):
- `Destination`: Đại diện cho một điểm đến với `id`, `name`, `country`, `description`
- `Attraction`: Đại diện cho điểm tham quan với `id`, `destination_id`, `name`
- `Hotel`: Đại diện cho khách sạn với `id`, `destination_id`, `name`

**Interfaces**:
- `ExternalApiClient`: Abstract interface định nghĩa contract cho external API clients
- Cho phép dễ dàng thay thế implementation (Geoapify → Google Places, etc.)

**Use Cases** (Business Logic):
- `SearchDestinations`: Tìm kiếm điểm đến, lọc theo country, loại trùng
- `GetDestinationInfo`: Lấy thông tin chi tiết một điểm đến
- `GetAttractions`: Geocode → Tìm điểm tham quan gần đó
- `GetNearbyHotels`: Geocode → Tìm khách sạn gần đó

#### **3. Infrastructure Layer** (`infrastructure/`)

**GeoapifyClient**:
- Implement `ExternalApiClient` interface
- Sử dụng `httpx.AsyncClient` để gọi Geoapify API
- Các phương thức chính:
  - `search(query)`: Tìm kiếm địa điểm qua Geocoding API
  - `geocode(query)`: Chuyển địa điểm thành tọa độ (lon, lat)
  - `attractions_near()`: Gọi Places API với category `tourism`
  - `hotels_near()`: Gọi Places API với category `accommodation.hotel`
- Map dữ liệu JSON từ API về Domain Entities

#### **4. Schemas Layer** (`schemas/`)
- Pydantic models cho API input/output validation
- `DestinationOut`, `AttractionOut`, `HotelOut`
- Tự động generate OpenAPI documentation

### Đặc Điểm Thiết Kế

✅ **Stateless**: Không có database nội bộ, mọi dữ liệu lấy từ external API  
✅ **Dependency Injection**: Use cases nhận clients qua constructor  
✅ **Async/Await**: Sử dụng async I/O cho tất cả API calls  
✅ **Error Handling**: Xử lý exceptions từ external APIs gracefully  
✅ **Testability**: Clean Architecture giúp dễ dàng unit test với mock clients  

---

## 🔌 API Endpoints

Service expose các endpoints sau qua prefix `/api/v1`:

### **1. Health Check**

```http
GET /health
```

**Response:**
```json
{
  "status": "ok"
}
```

### **2. Tìm Kiếm Điểm Đến**

```http
GET /api/v1/destinations?query={keyword}&country={country_code}
```

**Query Parameters:**
- `query` (required): Từ khóa tìm kiếm (e.g., "Paris", "Tokyo")
- `country` (optional): Lọc theo quốc gia (e.g., "France", "Japan")

**Response:** `200 OK`
```json
[
  {
    "id": "12345",
    "name": "Paris",
    "country": "France",
    "description": "Paris, Île-de-France, France"
  }
]
```

**Errors:**
- `500`: Missing GEOAPIFY_API_KEY

### **3. Lấy Chi Tiết Điểm Đến**

```http
GET /api/v1/destinations/{destination_query}
```

**Path Parameters:**
- `destination_query`: Chuỗi tìm kiếm điểm đến

**Response:** `200 OK`
```json
{
  "id": "12345",
  "name": "Paris",
  "country": "France",
  "description": "Paris, Île-de-France, France"
}
```

**Errors:**
- `404`: Destination not found
- `500`: Missing GEOAPIFY_API_KEY

### **4. Tìm Điểm Tham Quan**

```http
GET /api/v1/attractions?location={location}&radius_m={radius}&limit={limit}
```

**Query Parameters:**
- `location` (required): Tên địa điểm hoặc địa chỉ
- `radius_m` (optional, default=5000): Bán kính tìm kiếm (mét)
- `limit` (optional, default=20): Số kết quả tối đa

**Response:** `200 OK`
```json
[
  {
    "id": "attraction_123",
    "destination_id": "Paris",
    "name": "Eiffel Tower"
  }
]
```

### **5. Tìm Khách Sạn**

```http
GET /api/v1/hotels?location={location}&radius_m={radius}&limit={limit}
```

**Query Parameters:**
- `location` (required): Tên địa điểm hoặc địa chỉ
- `radius_m` (optional, default=5000): Bán kính tìm kiếm (mét)
- `limit` (optional, default=20): Số kết quả tối đa

**Response:** `200 OK`
```json
[
  {
    "id": "hotel_456",
    "destination_id": "Paris",
    "name": "Hotel de Paris"
  }
]
```

### **6. Tìm Kiếm Chung**

```http
GET /api/v1/search?query={keyword}&country={country_code}
```

Tương tự endpoint `/destinations`, dùng cho unified search.

---

## ⚙️ Giải Thích Hoạt Động

### **Flow 1: Tìm Kiếm Điểm Đến**

```
Client Request
    ↓
GET /api/v1/destinations?query=paris&country=France
    ↓
[destinations.py:list_destinations()]
    │
    ├─→ Kiểm tra GEOAPIFY_API_KEY
    │   (nếu thiếu → HTTPException 500)
    │
    ├─→ Khởi tạo GeoapifyClient(api_key)
    │
    ├─→ Khởi tạo SearchDestinations use case
    │
    └─→ use_case.execute(query="paris", country="France")
        ↓
    [search_destinations.py:SearchDestinations.execute()]
        │
        ├─→ Gọi client.search("paris") song song (asyncio.gather)
        │   ↓
        │   [geoapify_client.py:search()]
        │       │
        │       ├─→ httpx.get(geocode_url, params={text: "paris", ...})
        │       ├─→ Parse JSON response
        │       └─→ Map to Destination entities
        │
        ├─→ Lọc theo country nếu có (country.lower() == "france")
        │
        ├─→ Loại bỏ duplicate theo id (deduplication)
        │
        └─→ Trả về list[Destination]
            ↓
Map to list[DestinationOut] schema
    ↓
JSON Response
```

**File liên quan:**
- `src/api/v1/endpoints/destinations.py` (line 13-21)
- `src/core/use_cases/search_destinations.py` (line 14-37)
- `src/infrastructure/external/geoapify_client.py` (line 30-50)

### **Flow 2: Lấy Chi Tiết Điểm Đến**

```
GET /api/v1/destinations/{destination_query}
    ↓
[destinations.py:get_destination()]
    │
    ├─→ Kiểm tra GEOAPIFY_API_KEY
    ├─→ Khởi tạo GeoapifyClient
    ├─→ Khởi tạo GetDestinationInfo use case
    │
    └─→ use_case.execute(destination_query)
        ↓
    [get_destination_info.py:GetDestinationInfo.execute()]
        │
        ├─→ results = await client.search(destination_query)
        │       (Gọi Geoapify Geocoding API)
        │
        └─→ return results[0] if results else None
            ↓
    Nếu None → HTTPException 404
    Ngược lại → Map to DestinationOut
```

**File liên quan:**
- `src/api/v1/endpoints/destinations.py` (line 24-34)
- `src/core/use_cases/get_destination_info.py` (line 11-13)

### **Flow 3: Tìm Điểm Tham Quan**

```
GET /api/v1/attractions?location=Paris&radius_m=5000&limit=20
    ↓
[attractions.py:list_attractions()]
    │
    ├─→ Kiểm tra GEOAPIFY_API_KEY
    ├─→ Khởi tạo GetAttractions use case
    │
    └─→ use_case.execute(location, radius_m, limit)
        ↓
    [get_attractions.py:GetAttractions.execute()]
        │
        ├─→ coords = await client.geocode("Paris")
        │   ↓
        │   [geoapify_client.py:geocode()]
        │       │
        │       ├─→ httpx.get(geocode_url, params={text: "Paris"})
        │       └─→ return (lon, lat) từ first result
        │
        ├─→ Nếu coords is None → return []
        │
        └─→ await client.attractions_near(lon, lat, "Paris", radius_m, limit)
            ↓
        [geoapify_client.py:attractions_near()]
            │
            ├─→ Gọi _places(categories="tourism", lon, lat, radius, limit)
            │   ↓
            │   httpx.get(places_url, params={
            │       categories: "tourism",
            │       filter: "circle:lon,lat,5000",
            │       ...
            │   })
            │
            ├─→ Parse features từ response
            └─→ Map to Attraction entities
                ↓
Map to list[AttractionOut]
```

**File liên quan:**
- `src/api/v1/endpoints/attractions.py` (line 12-24)
- `src/core/use_cases/get_attractions.py` (line 11-16)
- `src/infrastructure/external/geoapify_client.py` (line 52-100)

### **Flow 4: Tìm Khách Sạn**

```
GET /api/v1/hotels?location=Paris&radius_m=5000&limit=20
    ↓
[hotels.py:list_hotels()]
    │
    └─→ use_case.execute(location, radius_m, limit)
        ↓
    [get_nearby_hotels.py:GetNearbyHotels.execute()]
        │
        ├─→ coords = await client.geocode("Paris")
        │
        └─→ await client.hotels_near(lon, lat, "Paris", radius_m, limit)
            ↓
        [geoapify_client.py:hotels_near()]
            │
            ├─→ Gọi _places(categories="accommodation.hotel", ...)
            │   (Tương tự attractions nhưng category khác)
            │
            └─→ Map to Hotel entities
```

**File liên quan:**
- `src/api/v1/endpoints/hotels.py` (line 12-24)
- `src/core/use_cases/get_nearby_hotels.py` (line 11-16)
- `src/infrastructure/external/geoapify_client.py` (line 102-121)

### **Các Thành Phần Quan Trọng**

#### **GeoapifyClient Implementation**

`src/infrastructure/external/geoapify_client.py`:

- **Method `_get()`**: Helper async method để gọi HTTP GET với httpx
- **Method `search()`**: Gọi Geocoding API `/v1/geocode/search`, map results to `Destination` entities
- **Method `geocode()`**: Chuyển địa điểm thành tọa độ (lon, lat)
- **Method `_places()`**: Generic method gọi Places API `/v2/places` với category filter
- **Method `attractions_near()`**: Wrapper gọi `_places()` với category `tourism`
- **Method `hotels_near()`**: Wrapper gọi `_places()` với category `accommodation.hotel`

#### **Settings Configuration**

`src/config/settings.py`:

```python
class Settings(BaseSettings):
    app_name: str = "destination-service"
    environment: str = "local"
    log_level: str = "INFO"
    database_url: str = "sqlite:///./destination.db"  # Not used
    redis_url: str = "redis://localhost:6379/0"        # Not used
    geoapify_api_key: str | None = None                # Required!
```

Sử dụng `pydantic_settings` để load từ `.env` file.

---

## 🚀 Cấu Hình và Triển Khai

### **1. Environment Variables**

Tạo file `.env` từ template:

```bash
cp .env.example .env
```

Cấu hình bắt buộc trong `.env`:

```bash
APP_NAME=destination-service
ENVIRONMENT=local
LOG_LEVEL=INFO
GEOAPIFY_API_KEY=your-geoapify-api-key-here  # Bắt buộc!
```

Lấy API key tại: https://www.geoapify.com/

### **2. Chạy Local (Development)**

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy với uvicorn
uvicorn src.main:app --reload --port 8000

# Truy cập Swagger docs
open http://localhost:8000/docs
```

### **3. Chạy với Docker**

Service được tích hợp trong docker-compose của hệ thống microservices.

```bash
# Từ thư mục gốc của trip-hub
docker compose up -d --build

# Kiểm tra health
curl http://localhost:9000/health
```

### **4. Gọi API qua Middleware**

Trong hệ thống microservices, service được gọi qua middleware gateway:

```bash
# Tìm kiếm điểm đến
curl "http://localhost:9000/api/v1/destination/destinations?query=paris"

# Lấy chi tiết
curl "http://localhost:9000/api/v1/destination/destinations/paris"

# Tìm điểm tham quan
curl "http://localhost:9000/api/v1/destination/attractions?location=paris&limit=10"

# Tìm khách sạn
curl "http://localhost:9000/api/v1/destination/hotels?location=paris&limit=10"
```

**Lưu ý**: Middleware forward requests từ `/api/v1/destination/*` đến service này.

### **5. API Documentation**

Khi service đang chạy:

- **Swagger UI**: http://localhost:8000/docs (local) hoặc qua middleware
- **ReDoc**: http://localhost:8000/redoc

### **6. Testing**

```bash
# Cài dev dependencies
pip install -r requirements-dev.txt

# Chạy tests (nếu có)
pytest tests/

# Type checking
mypy src/

# Linting
ruff check src/
```

---

## 📚 Dependencies

### Production (`requirements.txt`)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic-settings==2.1.0
httpx==0.25.2
```

### Development (`requirements-dev.txt`)
```
pytest==7.4.3
pytest-asyncio==0.21.1
mypy==1.7.1
ruff==0.1.6
```

---

## 🔍 Troubleshooting

### **Lỗi: Missing GEOAPIFY_API_KEY**

```json
{
  "detail": "Missing GEOAPIFY_API_KEY"
}
```

**Giải pháp**: Thêm `GEOAPIFY_API_KEY` vào file `.env`

### **Lỗi: Destination not found (404)**

Endpoint `/destinations/{destination_query}` trả về kết quả đầu tiên từ search. Nếu không tìm thấy → 404.

**Giải pháp**: Kiểm tra lại query string hoặc dùng endpoint `/destinations?query=...` để xem danh sách kết quả.

### **Lỗi: Connection timeout**

Geoapify API có thể chậm hoặc không khả dụng.

**Giải pháp**: 
- Kiểm tra internet connection
- Verify API key còn valid
- Tăng timeout trong `GeoapifyClient._get()` (hiện tại 10s)

---

## 📐 Kiến Trúc Tích Hợp

Service này là một phần của hệ thống microservices **Trip Hub**:

```
┌─────────────────────────────────────────────────┐
│           Middleware Service (Port 9000)         │
│              (API Gateway + Auth)               │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────┼────────────┬──────────────┐
    ↓            ↓            ↓              ↓
┌─────────┐  ┌─────────┐  ┌──────────┐  ┌─────────┐
│Destination│ │ Weather │ │Itinerary │ │ Booking │
│  Service  │ │ Service │ │ Service  │ │ Service │
└─────────┘  └────┬────┘  └────┬─────┘  └────┬────┘
                  │            │             │
              ┌───┴───┐    ┌───┴───┐    ┌───┴───┐
              │Postgres│    │Postgres│   │ Redis │
              └────────┘    └────────┘   └───────┘
```

**Vai trò**: Cung cấp dữ liệu điểm đến, điểm tham quan, khách sạn cho các services khác thông qua API Gateway.

---

## 📝 Notes

- Service **không lưu trữ dữ liệu** vào database, mọi thứ query trực tiếp từ Geoapify
- Sử dụng **async/await** cho tất cả external API calls để tối ưu performance
- **Deduplication** được thực hiện dựa trên `id` của entities
- Support **multiple external clients** qua interface abstraction (dễ dàng thêm Google Places, Mapbox, etc.)
- Service chạy trên **port 8000** internal, exposed qua middleware trên port 9000
