# Booking Service

**Booking Service** cung cấp khả năng tìm kiếm và đặt vé máy bay, khách sạn thông qua **Amadeus API**. Service tích hợp với Amadeus Test API để cung cấp dữ liệu thực tế về chuyến bay và khách sạn trên toàn thế giới.

---

## 📋 Mục Lục

1. [Phân Tích Yêu Cầu](#phân-tích-yêu-cầu)
2. [Thiết Kế Phần Mềm](#thiết-kế-phần-mềm)
3. [API Endpoints](#api-endpoints)
4. [Giải Thích Hoạt Động](#giải-thích-hoạt-động)
5. [Cấu Hình và Triển Khai](#cấu-hình-và-triển-khai)

---

## 📌 Phân Tích Yêu Cầu

Service cung cấp 3 nhóm chức năng chính, bám sát theo implementation hiện có:

### 1. **Flight Search (Tìm Kiếm Chuyến Bay)**

**Yêu cầu**:
- Tìm kiếm chuyến bay giữa 2 sân bay (origin → destination)
- Hỗ trợ cả chuyến bay một chiều và khứ hồi
- Filter theo hạng vé (Economy, Business, First Class)
- Filter chuyến bay thẳng (non-stop)
- Tìm kiếm với số lượng hành khách tùy chỉnh (1-9 adults)
- Hiển thị giá vé theo đơn vị tiền tệ mong muốn
- Giới hạn số lượng kết quả (max 250)
- Lấy chi tiết chuyến bay cụ thể theo offer ID

**Data từ**: Amadeus Flight Offers Search API v2

### 2. **Hotel Search (Tìm Kiếm Khách Sạn)**

**Yêu cầu**:
- Tìm kiếm khách sạn theo mã thành phố (city code)
- Tìm kiếm theo ngày check-in và check-out
- Hỗ trợ multiple rooms và guests (adults + children)
- Filter theo bán kính từ trung tâm thành phố
- Filter theo chính sách thanh toán và loại bữa ăn
- Hiển thị giá phòng, rating, amenities
- Lấy chi tiết offers của một khách sạn cụ thể

**Data từ**: 
- Amadeus Hotel Search API v1 (get hotels by city)
- Amadeus Hotel Offers API v3 (get pricing & availability)

### 3. **Cities Reference Data**

**Yêu cầu**:
- Cung cấp danh sách thành phố với mã IATA
- Hỗ trợ tìm kiếm theo tên thành phố hoặc mã IATA
- Filter theo mã quốc gia (country code)
- Giới hạn số lượng kết quả
- Lấy thông tin chi tiết một thành phố theo IATA code

**Data từ**: Hardcoded list (50+ major cities worldwide)

### 4. **Amadeus API Authentication**

**Yêu cầu**:
- OAuth2 Client Credentials flow
- Automatic access token management
- Token caching với expiration tracking
- Auto-refresh token khi hết hạn
- Error handling cho authentication failures

**Implementation**: 
- Access token được cache trong memory
- Token expires sau ~30 phút (1799 seconds)
- Auto-refresh 60 seconds trước khi expire

---

## 🏗️ Thiết Kế Phần Mềm

Service được thiết kế theo **Clean Architecture** với sự tách biệt rõ ràng giữa các layers:

```
src/
├── main.py                          # Entry point, FastAPI app
├── config/
│   ├── settings.py                  # Configuration (Amadeus credentials, Redis)
│   └── logging.py                   # Logging setup
├── api/
│   └── v1/
│       ├── router.py                # Router aggregation
│       └── endpoints/
│           ├── flights.py           # Flight search endpoints
│           ├── hotels.py            # Hotel search endpoints
│           └── cities.py            # Cities reference endpoints
├── core/
│   ├── entities/
│   │   ├── flight.py                # Flight domain entities
│   │   └── hotel.py                 # Hotel domain entities
│   └── use_cases/
│       ├── search_flights.py        # Flight search business logic
│       └── search_hotels.py         # Hotel search business logic
├── infrastructure/
│   └── external/
│       └── amadeus_client.py        # Amadeus API client
└── schemas/
    ├── flight.py                    # Pydantic schemas for flights
    ├── hotel.py                     # Pydantic schemas for hotels
    └── city.py                      # Pydantic schemas for cities
```

### Kiến Trúc Chi Tiết

#### **1. Main Application** (`main.py`)

**Khởi tạo FastAPI**:
```python
app = FastAPI(
    title="Booking Service",
    version="1.0.0",
    description="Booking Service - Tìm kiếm và đặt vé máy bay, khách sạn",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)
```

**CORS Middleware**:
- Allow all origins (development mode)
- Allow credentials, all methods, all headers

**Startup Event**:
- Tạo thư mục `logs/` để lưu application logs
- Log service startup với name và version

#### **2. Configuration** (`config/settings.py`)

**Settings với Pydantic**:
```python
class Settings(BaseSettings):
    app_name: str = "Booking Service"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Amadeus API credentials
    amadeus_api_key: str
    amadeus_api_secret: str
    amadeus_base_url: str = "https://test.api.amadeus.com"
    
    # Redis caching (optional)
    redis_host: str = "localhost"
    redis_port: int = 6379
    cache_ttl: int = 3600
```

**Features**:
- Load from `.env` file
- Cached với `@lru_cache()` - singleton pattern
- Type-safe configuration

#### **3. Amadeus API Client** (`infrastructure/external/amadeus_client.py`)

**Responsibility**: Tích hợp với Amadeus API, quản lý authentication và HTTP requests.

**Key Components**:

**Authentication Flow**:
```python
async def _get_access_token(self) -> str:
    # Check if token is still valid
    if self._access_token and self._token_expires_at:
        if datetime.now() < self._token_expires_at:
            return self._access_token
    
    # Request new token via OAuth2 Client Credentials
    url = f"{self.base_url}/v1/security/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": self.api_key,
        "client_secret": self.api_secret
    }
    
    # Cache token with expiration (expires_in - 60 seconds buffer)
```

**Flight Search**:
```python
async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int = 1,
    return_date: Optional[str] = None,
    travel_class: Optional[str] = None,
    non_stop: bool = False,
    currency: str = "USD",
    max_results: int = 10
) -> Dict[str, Any]:
    # GET /v2/shopping/flight-offers
```

**Hotel Search (2-step process)**:
1. `get_hotels_by_city()`: Lấy danh sách hotel IDs trong thành phố
2. `search_hotels()`: Lấy pricing & availability cho hotel IDs

**Error Handling**:
- Catch `httpx.HTTPError`
- Log error details including response text
- Raise descriptive exceptions

#### **4. Use Cases** (`core/use_cases/`)

**SearchFlightsUseCase**:
```python
class SearchFlightsUseCase:
    def __init__(self, amadeus_client: AmadeusClient):
        self.amadeus_client = amadeus_client
    
    async def execute(self, search_request: FlightSearchRequest):
        # Delegate to Amadeus client
        # Log search details
        # Return raw Amadeus response
```

**SearchHotelsUseCase**:
```python
class SearchHotelsUseCase:
    def __init__(self, amadeus_client: AmadeusClient):
        self.amadeus_client = amadeus_client
    
    async def execute(self, search_request: HotelSearchRequest):
        # Delegate to Amadeus client with optional parameters
        # Handle defaults for children, rooms, radius, etc.
```

**Note**: Use cases hiện tại khá "thin" - chủ yếu là delegation. Trong production có thể thêm:
- Response transformation
- Business rules validation
- Caching logic
- Rate limiting

#### **5. Domain Entities** (`core/entities/`)

**FlightEntity**:
```python
@dataclass
class FlightEntity:
    id: str
    source: str
    one_way: bool
    segments: List[Segment]
    price: Price
    validating_airline_codes: List[str]
    
    def get_total_duration(self) -> str
    def is_direct_flight(self) -> bool
    def get_total_stops(self) -> int
```

**HotelEntity**:
```python
@dataclass
class HotelEntity:
    hotel_id: str
    name: str
    city_code: str
    rating: Optional[str]
    location: Optional[HotelLocation]
    amenities: List[HotelAmenity]
    rooms: List[Room]
    
    def get_min_price(self) -> Optional[float]
    def has_amenity(self, amenity_name: str) -> bool
    def get_distance_from(self, lat: float, lon: float) -> float
```

**Features**:
- Immutable dataclasses
- Business logic methods (get_min_price, is_direct_flight, etc.)
- Type safety với Python typing

#### **6. API Schemas** (`schemas/`)

**FlightSearchRequest**:
```python
class FlightSearchRequest(BaseModel):
    origin: str = Field(..., min_length=3, max_length=3)
    destination: str = Field(..., min_length=3, max_length=3)
    departure_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    return_date: str
    adults: int = Field(..., ge=1, le=9)
    currency: str
    travel_class: Optional[str] = None
    non_stop: Optional[bool] = False
    max_results: Optional[int] = Field(10, ge=1, le=250)
```

**HotelSearchRequest**:
```python
class HotelSearchRequest(BaseModel):
    city_code: str = Field(..., min_length=3, max_length=3)
    check_in_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    check_out_date: str
    adults: int = Field(..., ge=1, le=9)
    children: Optional[int] = Field(0, ge=0, le=9)
    rooms: Optional[int] = Field(1, ge=1, le=9)
    radius: Optional[int] = Field(5, ge=1, le=300)
    currency: Optional[str] = Field("USD")
```

**Validation Features**:
- IATA code validation (3 characters)
- Date format validation (YYYY-MM-DD)
- Numeric ranges (adults: 1-9, rooms: 1-9)
- Optional parameters with defaults
- OpenAPI documentation examples

#### **7. API Endpoints** (`api/v1/endpoints/`)

**Dependency Injection Pattern**:
```python
def get_amadeus_client() -> AmadeusClient:
    return AmadeusClient()

def get_search_flights_use_case(
    amadeus_client: AmadeusClient = Depends(get_amadeus_client)
) -> SearchFlightsUseCase:
    return SearchFlightsUseCase(amadeus_client)

@router.post("/search")
async def search_flights(
    search_request: FlightSearchRequest,
    use_case: SearchFlightsUseCase = Depends(get_search_flights_use_case)
):
    result = await use_case.execute(search_request)
    return result
```

**Benefits**:
- Testability (easy to mock dependencies)
- Separation of concerns
- Clean code structure

### Đặc Điểm Thiết Kế

✅ **Clean Architecture**: Tách biệt rõ ràng giữa API, Business Logic, và External Integration  
✅ **Dependency Injection**: FastAPI Depends pattern  
✅ **Type Safety**: Pydantic schemas, Python type hints  
✅ **Token Management**: Automatic OAuth2 token refresh  
✅ **Error Handling**: Comprehensive error catching và logging  
✅ **Async/Await**: Full async support với httpx  
✅ **OpenAPI Documentation**: Auto-generated Swagger UI  
⚠️ **No Caching**: Redis config available nhưng chưa implement  
⚠️ **No Database**: Stateless service, không lưu bookings

---

## 🔌 API Endpoints

Service expose các endpoints qua prefix `/api/v1`:

### **1. Flight Endpoints**

#### **Search Flights**

```http
POST /api/v1/flights/search
Content-Type: application/json

{
  "origin": "HAN",
  "destination": "BKK", 
  "departure_date": "2025-02-15",
  "return_date": "2025-02-20",
  "adults": 2,
  "currency": "USD",
  "travel_class": "ECONOMY",
  "non_stop": false,
  "max_results": 10
}
```

**Response:** `200 OK`
```json
{
  "meta": {
    "count": 10
  },
  "data": [
    {
      "id": "1",
      "source": "GDS",
      "price": {
        "currency": "USD",
        "total": "250.00",
        "base": "200.00",
        "grand_total": "250.00"
      },
      "itineraries": [...]
    }
  ]
}
```

**Parameters**:
- `origin` (required): IATA code sân bay xuất phát (VD: HAN, SGN)
- `destination` (required): IATA code sân bay đến
- `departure_date` (required): Ngày đi (YYYY-MM-DD)
- `return_date` (required): Ngày về
- `adults` (required): Số hành khách (1-9)
- `currency` (required): Đơn vị tiền tệ (USD, EUR, VND, etc.)
- `travel_class` (optional): ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST
- `non_stop` (optional): true = chỉ chuyến bay thẳng
- `max_results` (optional): Số kết quả (1-250, default: 10)

#### **Get Flight Offer Details**

```http
GET /api/v1/flights/{offer_id}
```

**Response:** Flight offer details

#### **Flight Health Check**

```http
GET /api/v1/flights/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "flight-search",
  "version": "1.0.0"
}
```

### **2. Hotel Endpoints**

#### **Search Hotels**

```http
POST /api/v1/hotels/search
Content-Type: application/json

{
  "city_code": "BKK",
  "check_in_date": "2025-02-01",
  "check_out_date": "2025-02-05",
  "adults": 2,
  "children": 1,
  "rooms": 1,
  "radius": 10,
  "currency": "USD",
  "max_results": 10
}
```

**Response:** `200 OK`
```json
{
  "data": [
    {
      "type": "hotel-offers",
      "hotel": {
        "hotelId": "BKXXX001",
        "name": "Grand Hotel Bangkok",
        "rating": "5",
        "cityCode": "BKK"
      },
      "available": true,
      "offers": [
        {
          "id": "OFFER123",
          "price": {
            "currency": "USD",
            "total": "150.00"
          }
        }
      ]
    }
  ],
  "meta": {
    "count": 10
  }
}
```

**Parameters**:
- `city_code` (required): Mã IATA thành phố (BKK, SIN, NYC)
- `check_in_date` (required): Ngày nhận phòng (YYYY-MM-DD)
- `check_out_date` (required): Ngày trả phòng
- `adults` (required): Số người lớn (1-9)
- `children` (optional): Số trẻ em (0-9, default: 0)
- `rooms` (optional): Số phòng (1-9, default: 1)
- `radius` (optional): Bán kính tìm kiếm (km, 1-300, default: 5)
- `currency` (optional): Đơn vị tiền tệ (default: USD)
- `payment_policy` (optional): GUARANTEE, DEPOSIT, NONE
- `board_type` (optional): ROOM_ONLY, BREAKFAST, HALF_BOARD, FULL_BOARD
- `max_results` (optional): Số kết quả (1-100, default: 10)

#### **Get Hotel Offers**

```http
POST /api/v1/hotels/offers
Content-Type: application/json

{
  "hotel_id": "BKXXX001",
  "check_in_date": "2025-02-01",
  "check_out_date": "2025-02-05",
  "adults": 2,
  "rooms": 1,
  "currency": "USD"
}
```

**Response:** Hotel offers với room types và pricing

#### **Hotel Health Check**

```http
GET /api/v1/hotels/health
```

### **3. Cities Endpoints**

#### **List Cities**

```http
GET /api/v1/cities?keyword={search}&country_code={code}&limit={n}
```

**Query Parameters**:
- `keyword` (optional): Tìm kiếm theo tên hoặc IATA code
- `country_code` (optional): Filter theo mã quốc gia (VN, TH, US)
- `limit` (optional): Số kết quả max (1-100, default: 50)

**Response:** `200 OK`
```json
{
  "data": [
    {
      "iata_code": "BKK",
      "name": "Bangkok",
      "country": "Thailand",
      "country_code": "TH"
    }
  ],
  "meta": {
    "count": 1,
    "total": 50,
    "limit": 50
  }
}
```

#### **Get City by IATA Code**

```http
GET /api/v1/cities/{iata_code}
```

**Example**: `GET /api/v1/cities/BKK`

**Response:** City details

#### **Cities Health Check**

```http
GET /api/v1/cities/health
```

### **4. Root Endpoints**

#### **Root**

```http
GET /
```

**Response:**
```json
{
  "service": "Booking Service",
  "version": "1.0.0",
  "status": "running",
  "docs": "/api/docs"
}
```

#### **Health**

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Booking Service",
  "version": "1.0.0"
}
```

---

## ⚙️ Giải Thích Hoạt Động

### **Flow 1: Flight Search with Amadeus API**

```
Client Request
    ↓
POST /api/v1/flights/search
{
  origin: "HAN",
  destination: "BKK",
  departure_date: "2025-02-15",
  return_date: "2025-02-20",
  adults: 2,
  currency: "USD"
}
    ↓
[flights.py:search_flights()] ← Controller
    │
    ├─→ Pydantic validation
    │   FlightSearchRequest validates input
    │   - IATA codes: 3 characters
    │   - Date format: YYYY-MM-DD
    │   - Adults: 1-9
    │   ↓
    │   Validation passed
    │
    ├─→ Dependency Injection
    │   get_amadeus_client() → AmadeusClient instance
    │   get_search_flights_use_case() → SearchFlightsUseCase(client)
    │   ↓
    │
    └─→ Execute use case
        use_case.execute(search_request)
        ↓
    [search_flights.py:SearchFlightsUseCase.execute()]
        │
        └─→ Delegate to Amadeus client
            amadeus_client.search_flights(
                origin="HAN",
                destination="BKK",
                ...
            )
            ↓
    [amadeus_client.py:AmadeusClient.search_flights()]
        │
        ├─→ Get access token
        │   token = await self._get_access_token()
        │   ↓
        │   [_get_access_token()]
        │       │
        │       ├─→ Check cached token
        │       │   if self._access_token and datetime.now() < self._token_expires_at:
        │       │       return self._access_token  # Token still valid
        │       │
        │       └─→ Request new token (OAuth2)
        │           POST https://test.api.amadeus.com/v1/security/oauth2/token
        │           {
        │             grant_type: "client_credentials",
        │             client_id: "vufTw1626D0b6oBAOc4imErAWpvEGVFR",
        │             client_secret: "dCILSPjIHv40Hyfg"
        │           }
        │           ↓
        │           Response: {
        │             "access_token": "abc123...",
        │             "expires_in": 1799
        │           }
        │           ↓
        │           Cache token:
        │           self._access_token = "abc123..."
        │           self._token_expires_at = now + timedelta(seconds=1739)  # 60s buffer
        │           ↓
        │           return "abc123..."
        │
        ├─→ Build Amadeus API request
        │   url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        │   headers = {"Authorization": "Bearer abc123..."}
        │   params = {
        │       "originLocationCode": "HAN",
        │       "destinationLocationCode": "BKK",
        │       "departureDate": "2025-02-15",
        │       "returnDate": "2025-02-20",
        │       "adults": 2,
        │       "currencyCode": "USD",
        │       "max": 10
        │   }
        │
        ├─→ Send HTTP request
        │   async with httpx.AsyncClient(timeout=30.0) as client:
        │       response = await client.get(url, headers=headers, params=params)
        │       response.raise_for_status()
        │   ↓
        │   Amadeus returns flight offers (may take 5-10 seconds)
        │
        └─→ Return raw Amadeus response
            {
              "meta": {"count": 10},
              "data": [
                {
                  "id": "1",
                  "source": "GDS",
                  "price": {
                    "currency": "USD",
                    "total": "250.00",
                    ...
                  },
                  "itineraries": [...]
                }
              ]
            }
            ↓
    Return to client (200 OK)
```

**File liên quan:**
- `src/api/v1/endpoints/flights.py` (line 57-73)
- `src/core/use_cases/search_flights.py` (line 13-34)
- `src/infrastructure/external/amadeus_client.py` (line 51-102, 19-49)
- `src/schemas/flight.py` (line 6-30)

**Key Points**:
1. **Token Caching**: Token chỉ được request khi cần (expired hoặc không tồn tại)
2. **Async All The Way**: Full async từ endpoint → use case → HTTP client
3. **No Transformation**: Response từ Amadeus được trả về nguyên gốc
4. **Error Propagation**: Exceptions từ Amadeus được catch và re-raise với message rõ ràng

### **Flow 2: Hotel Search (2-Step Process)**

```
POST /api/v1/hotels/search
{
  city_code: "BKK",
  check_in_date: "2025-02-01",
  check_out_date: "2025-02-05",
  adults: 2,
  children: 1,
  rooms: 1
}
    ↓
[hotels.py:search_hotels()]
    ↓
[search_hotels.py:SearchHotelsUseCase.execute()]
    ↓
[amadeus_client.py:AmadeusClient.search_hotels()]
    │
    ├─→ Step 1: Get hotel IDs by city
    │   hotels_data = await self.get_hotels_by_city("BKK", radius=5, unit="KM")
    │   ↓
    │   [get_hotels_by_city()]
    │       GET /v1/reference-data/locations/hotels/by-city
    │       params = {"cityCode": "BKK", "radius": 5, "radiusUnit": "KM"}
    │       ↓
    │       Response: {
    │         "data": [
    │           {"hotelId": "BKXXX001", "name": "Grand Hotel", ...},
    │           {"hotelId": "BKXXX002", "name": "Luxury Resort", ...},
    │           ...
    │         ]
    │       }
    │       ↓
    │   Extract hotel IDs: ["BKXXX001", "BKXXX002", ...]
    │   Limit to max_results (10)
    │
    ├─→ Step 2: Get hotel offers (pricing & availability)
    │   hotel_ids = ",".join(["BKXXX001", "BKXXX002", ...])
    │   ↓
    │   GET /v3/shopping/hotel-offers
    │   params = {
    │       "hotelIds": "BKXXX001,BKXXX002,...",
    │       "checkInDate": "2025-02-01",
    │       "checkOutDate": "2025-02-05",
    │       "adults": 2,
    │       "roomQuantity": 1,
    │       "currency": "USD",
    │       "bestRateOnly": "true"
    │   }
    │   ↓
    │   Response: {
    │     "data": [
    │       {
    │         "type": "hotel-offers",
    │         "hotel": {
    │           "hotelId": "BKXXX001",
    │           "name": "Grand Hotel Bangkok",
    │           "rating": "5"
    │         },
    │         "offers": [
    │           {
    │             "id": "OFFER123",
    │             "price": {"currency": "USD", "total": "150.00"}
    │           }
    │         ]
    │       }
    │     ]
    │   }
    │
    └─→ Return combined response
```

**File liên quan:**
- `src/api/v1/endpoints/hotels.py` (line 68-84)
- `src/core/use_cases/search_hotels.py` (line 13-38)
- `src/infrastructure/external/amadeus_client.py` (line 126-228)

**Why 2-Step Process?**
1. Amadeus Hotel Offers API requires hotel IDs (không accept city code trực tiếp)
2. Step 1 lấy danh sách hotels trong thành phố
3. Step 2 lấy pricing & availability cho hotels đó

**Performance**: Có thể slow do 2 API calls tuần tự, nhưng đây là limitation của Amadeus API design.

### **Flow 3: Cities Reference Data (In-Memory)**

```
GET /api/v1/cities?keyword=bangkok&country_code=TH&limit=10
    ↓
[cities.py:get_cities()]
    │
    ├─→ Start with full list
    │   filtered_cities = CITIES_DATA.copy()  # 50+ cities
    │
    ├─→ Filter by country code (if provided)
    │   if country_code == "TH":
    │       filtered_cities = [city for city in filtered_cities 
    │                          if city["country_code"] == "TH"]
    │   ↓
    │   Result: [HAN, SGN, DAD, BKK, ...]
    │
    ├─→ Filter by keyword (if provided)
    │   if keyword == "bangkok":
    │       filtered_cities = [city for city in filtered_cities
    │                          if "bangkok" in city["name"].lower() 
    │                          or "bangkok" in city["iata_code"].lower()]
    │   ↓
    │   Result: [BKK]
    │
    ├─→ Apply limit
    │   filtered_cities = filtered_cities[:10]
    │
    └─→ Return response
        {
          "data": [{"iata_code": "BKK", "name": "Bangkok", ...}],
          "meta": {"count": 1, "total": 1, "limit": 10}
        }
```

**File liên quan:**
- `src/api/v1/endpoints/cities.py` (line 98-144)

**Note**: Cities data là hardcoded list (50+ major cities), không gọi external API. Đây là để tránh phụ thuộc vào Amadeus API cho reference data cơ bản.

### **Flow 4: Token Auto-Refresh**

```
[AmadeusClient._get_access_token()]
    │
    ├─→ Check if token exists and is valid
    │   if self._access_token and self._token_expires_at:
    │       if datetime.now() < self._token_expires_at:
    │           ✅ Return cached token (no API call)
    │
    └─→ Token expired or doesn't exist
        │
        ├─→ Request new token
        │   POST /v1/security/oauth2/token
        │   Content-Type: application/x-www-form-urlencoded
        │   Body: grant_type=client_credentials&client_id=...&client_secret=...
        │   ↓
        │   Response: {
        │     "access_token": "new_token_xyz",
        │     "expires_in": 1799,  # ~30 minutes
        │     "token_type": "Bearer"
        │   }
        │
        ├─→ Cache token with buffer
        │   self._access_token = "new_token_xyz"
        │   self._token_expires_at = datetime.now() + timedelta(seconds=1739)
        │   # 1799 - 60 = 1739 seconds (1 minute buffer)
        │
        └─→ Return new token
```

**Benefits**:
- Minimize authentication requests
- Automatic refresh before expiration
- No manual token management required
- Thread-safe (single instance per client)

---

## 🚀 Cấu Hình và Triển Khai

### **1. Environment Variables**

Tạo file `.env` từ template:

```bash
cp .env.example .env
```

Cấu hình trong `.env`:

```bash
APP_NAME=Booking Service
APP_VERSION=1.0.0
DEBUG=True

# Amadeus API credentials (Test environment)
AMADEUS_API_KEY=vufTw1626D0b6oBAOc4imErAWpvEGVFR
AMADEUS_API_SECRET=dCILSPjIHv40Hyfg
AMADEUS_BASE_URL=https://test.api.amadeus.com

# Redis caching (optional - not implemented yet)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL=3600
```

### **2. Chạy Local (Development)**

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy với uvicorn
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Hoặc chạy trực tiếp
cd src
python main.py
```

**Truy cập**:
- **API Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health**: http://localhost:8000/health

### **3. Chạy với Docker**

Service được tích hợp trong docker-compose của hệ thống:

```bash
# Từ thư mục gốc của trip-hub
docker compose up -d --build

# Kiểm tra booking service health
curl http://localhost:8000/health
```

### **4. Test API Examples**

#### **Flight Search**

```bash
curl -X POST "http://localhost:8000/api/v1/flights/search" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "HAN",
    "destination": "BKK",
    "departure_date": "2025-02-15",
    "return_date": "2025-02-20",
    "adults": 2,
    "currency": "USD",
    "travel_class": "ECONOMY",
    "max_results": 5
  }'
```

#### **Hotel Search**

```bash
curl -X POST "http://localhost:8000/api/v1/hotels/search" \
  -H "Content-Type: application/json" \
  -d '{
    "city_code": "BKK",
    "check_in_date": "2025-02-01",
    "check_out_date": "2025-02-05",
    "adults": 2,
    "rooms": 1,
    "currency": "USD",
    "max_results": 5
  }'
```

#### **List Cities**

```bash
# Get all cities
curl "http://localhost:8000/api/v1/cities?limit=50"

# Search by keyword
curl "http://localhost:8000/api/v1/cities?keyword=bangkok"

# Filter by country
curl "http://localhost:8000/api/v1/cities?country_code=VN"

# Get specific city
curl "http://localhost:8000/api/v1/cities/BKK"
```

---

## 📚 Dependencies

### Production (`requirements.txt`)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
httpx==0.25.2
pydantic-settings==2.1.0
python-dotenv==1.0.0
```

**Key Libraries**:
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `httpx`: Async HTTP client cho Amadeus API
- `pydantic-settings`: Configuration management
- `python-dotenv`: Load environment variables

---

## 🔍 Troubleshooting

### **Lỗi: Authentication failed**

```
Exception: Authentication failed: ...
```

**Nguyên nhân**: Amadeus API credentials không hợp lệ hoặc expired

**Giải pháp**:
- Verify `AMADEUS_API_KEY` và `AMADEUS_API_SECRET` trong `.env`
- Check Amadeus API status: https://developers.amadeus.com/status
- Credentials hiện tại là Test API, có giới hạn quota

### **Lỗi: Flight search failed**

```json
{
  "detail": "Lỗi khi tìm kiếm chuyến bay: ..."
}
```

**Nguyên nhân**: 
- IATA codes không hợp lệ
- Dates trong quá khứ
- Amadeus API quota exceeded

**Giải pháp**:
- Verify IATA codes (3 characters, uppercase)
- Check date format (YYYY-MM-DD)
- Ensure departure_date > today
- Check Amadeus quota limits

### **Lỗi: No hotels found in city**

```json
{
  "data": [],
  "meta": {"count": 0}
}
```

**Nguyên nhân**: City code không hợp lệ hoặc không có hotels trong Amadeus test data

**Giải pháp**:
- Verify city code (BKK, SIN, NYC, PAR, LON work well)
- Try larger radius (default: 5 KM)
- Some cities may not have test data in Amadeus

### **Lỗi: Request timeout**

```
httpx.TimeoutException
```

**Nguyên nhân**: Amadeus API slow response (timeout: 30s)

**Giải pháp**:
- Amadeus Test API có thể chậm vào giờ cao điểm
- Retry request
- Reduce `max_results` để giảm response size

### **Lỗi: Invalid date format**

```json
{
  "detail": [
    {
      "loc": ["body", "departure_date"],
      "msg": "string does not match regex",
      "type": "value_error.str.regex"
    }
  ]
}
```

**Nguyên nhân**: Date format không đúng

**Giải pháp**: Sử dụng format YYYY-MM-DD (VD: 2025-02-15)

---

## 🌍 IATA Codes Reference

### **Major Airports (Flights)**

**Vietnam**:
- HAN - Nội Bài, Hanoi
- SGN - Tân Sơn Nhất, Ho Chi Minh City
- DAD - Đà Nẵng, Da Nang

**Southeast Asia**:
- BKK - Suvarnabhumi, Bangkok, Thailand
- SIN - Changi, Singapore
- KUL - Kuala Lumpur International, Malaysia
- MNL - Ninoy Aquino, Manila, Philippines
- JKT - Soekarno-Hatta, Jakarta, Indonesia

**East Asia**:
- HKG - Hong Kong International
- TPE - Taiwan Taoyuan, Taipei
- TYO - Tokyo (all airports), Japan
- OSA - Osaka (all airports), Japan
- SEL - Seoul (all airports), South Korea
- PEK - Beijing Capital, China
- SHA - Shanghai (all airports), China

**Europe**:
- LON - London (all airports), UK
- PAR - Paris (all airports), France
- ROM - Rome (all airports), Italy
- BCN - Barcelona, Spain
- MAD - Madrid, Spain
- BER - Berlin, Germany
- AMS - Amsterdam, Netherlands

**Americas**:
- NYC - New York (all airports), USA
- LAX - Los Angeles, USA
- SFO - San Francisco, USA
- CHI - Chicago (all airports), USA
- YTO - Toronto (all airports), Canada
- MEX - Mexico City, Mexico

**Oceania**:
- SYD - Sydney, Australia
- MEL - Melbourne, Australia
- AKL - Auckland, New Zealand

### **Major Cities (Hotels)**

Service hỗ trợ 50+ cities worldwide. Sử dụng same IATA code như airports.

**Popular cities for hotel search**:
- BKK (Bangkok)
- SIN (Singapore)
- NYC (New York)
- PAR (Paris)
- LON (London)
- TYO (Tokyo)
- HKG (Hong Kong)
- DXB (Dubai)

---

## 📝 Notes

### **Amadeus Test API Limitations**

- **Free tier**: Limited quota per month
- **Rate limits**: ~5 requests/second
- **Test data**: Không phải tất cả routes/hotels có data
- **Expired offers**: Some offers may be unavailable khi book
- **No actual booking**: Test API không cho phép booking thực sự

### **Service Characteristics**

✅ **Stateless**: Không lưu bookings, chỉ search  
✅ **Real-time**: All data từ Amadeus API (not cached)  
✅ **Async**: Full async/await support  
✅ **Type-safe**: Pydantic validation  
⚠️ **No caching**: Redis config có nhưng chưa implement  
⚠️ **No booking**: Chỉ search, không có booking flow  
⚠️ **No payment**: Không tích hợp payment gateway  

### **Architecture Notes**

- **Clean Architecture**: Clear separation of concerns
- **Dependency Injection**: FastAPI Depends pattern
- **Thin Use Cases**: Mostly delegation (có thể thêm business logic)
- **No Database**: Pure API proxy service
- **Token Management**: Automatic OAuth2 handling
- **Error Propagation**: Exceptions bubbled up với clear messages

---

## 🎯 Future Improvements

### **1. Caching Layer**

```python
# Implement Redis caching for search results
@cache(ttl=3600)
async def search_flights(...):
    # Cache key: origin-destination-date-adults
    # Reduces Amadeus API calls
    # Improves response time
```

### **2. Rate Limiting**

```python
# Prevent API quota exhaustion
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.post("/flights/search")
@limiter.limit("10/minute")
async def search_flights(...):
    ...
```

### **3. Response Transformation**

```python
# Transform Amadeus response to simpler format
class SimplifiedFlightOffer:
    airline: str
    departure_time: datetime
    arrival_time: datetime
    duration: str
    price: float
    stops: int
```

### **4. Booking Flow**

- Implement booking creation (POST /bookings)
- Payment gateway integration (Stripe, PayPal)
- Booking confirmation emails
- Booking history storage (database)

### **5. Advanced Search Features**

- Multi-city flights
- Flexible dates (±3 days)
- Price alerts
- Seat selection
- Baggage options
- Meal preferences

### **6. Testing**

```python
# Unit tests
pytest tests/unit/

# Integration tests with mocked Amadeus
pytest tests/integration/

# E2E tests
pytest tests/e2e/
```

### **7. Monitoring & Observability**

- Request tracing (OpenTelemetry)
- Metrics collection (Prometheus)
- Error tracking (Sentry)
- Performance monitoring (New Relic)

### **8. Additional Features**

- Car rental search
- Airport transfers
- Activities & tours
- Travel insurance
- Visa requirements
- Currency conversion
- Multi-language support

---

## � Tích Hợp với Middleware

Service được truy cập qua Middleware Service (API Gateway):

```
Client
  ↓
Middleware Service (Port 9000) - JWT Auth
  ↓
Booking Service (Port 8000) - Internal
  ↓
Amadeus API
```

**Proxy Routes via Middleware**:
```bash
# Thay vì gọi trực tiếp
POST http://booking-service:8000/api/v1/flights/search

# Client gọi qua middleware
POST http://localhost:9000/api/v1/booking/flights/search
Authorization: Bearer <JWT_TOKEN>
```

**Benefits**:
- Centralized authentication
- Rate limiting at gateway level
- Request logging
- Service abstraction

---

## 🚀 Quick Start Guide

### **1. Tìm kiếm chuyến bay HAN → BKK**

```bash
# 1. Start service
uvicorn src.main:app --reload

# 2. Search flights
curl -X POST "http://localhost:8000/api/v1/flights/search" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "HAN",
    "destination": "BKK",
    "departure_date": "2025-03-01",
    "return_date": "2025-03-07",
    "adults": 1,
    "currency": "USD"
  }'

# 3. View results in Swagger UI
# Open: http://localhost:8000/api/docs
```

### **2. Tìm kiếm khách sạn ở Bangkok**

```bash
# 1. Search hotels
curl -X POST "http://localhost:8000/api/v1/hotels/search" \
  -H "Content-Type: application/json" \
  -d '{
    "city_code": "BKK",
    "check_in_date": "2025-03-01",
    "check_out_date": "2025-03-07",
    "adults": 2,
    "rooms": 1,
    "currency": "USD"
  }'
```

### **3. Browse cities**

```bash
# List all cities
curl "http://localhost:8000/api/v1/cities"

# Search cities
curl "http://localhost:8000/api/v1/cities?keyword=paris"
```

---

## � Additional Documentation

Xem thêm:
- **HOTEL_SEARCH_GUIDE.md**: Chi tiết về hotel search API
- **USAGE.md**: Ví dụ sử dụng thực tế
- **DOCKER.md**: Docker deployment guide
- **Amadeus API Docs**: https://developers.amadeus.com/

---

**Service Status**: ✅ Production Ready (with Test API)  
**Last Updated**: December 2024  
**Maintainer**: Trip Hub Team
