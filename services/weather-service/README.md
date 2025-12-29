# Weather Service

Microservice cung cấp thông tin thời tiết hiện tại và dự báo thời tiết sử dụng OpenWeatherMap API. Được xây dựng theo Clean Architecture với FastAPI.

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

### 1. **Lấy Thời Tiết Hiện Tại**
- Lấy thông tin thời tiết hiện tại theo tên địa điểm (thành phố, khu vực)
- Trả về thông tin: `location`, `temperature` (°C), `description` (mô tả thời tiết)
- Sử dụng OpenWeatherMap API endpoint `/weather`
- Temperature được trả về theo đơn vị metric (Celsius)

### 2. **Lấy Dự Báo Thời Tiết**
- Lấy dự báo thời tiết nhiều ngày cho một địa điểm
- Trả về danh sách các bản ghi `WeatherOut` với forecast data
- Sử dụng OpenWeatherMap API endpoint `/forecast`
- Mỗi item trong danh sách đại diện cho một thời điểm dự báo

### 3. **Yêu Cầu Bắt Buộc**
- Bắt buộc phải cấu hình `OPENWEATHER_API_KEY` trong file `.env`
- Thiếu API key sẽ trả về lỗi 500 Internal Server Error
- API key không hợp lệ sẽ trả về lỗi 401 Unauthorized
- Không sử dụng cache nội bộ, dữ liệu được lấy trực tiếp từ OpenWeather API

### 4. **Error Handling**
- Xử lý lỗi từ OpenWeather API (401, 404, 5xx)
- Map các lỗi HTTP status thành HTTPException phù hợp
- Cung cấp error messages rõ ràng cho client

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
│           ├── weather.py           # Current weather endpoint
│           └── forecast.py          # Forecast endpoint
├── core/
│   ├── entities/
│   │   └── weather.py               # Weather domain entity
│   ├── interfaces/                  # Abstract interfaces (if any)
│   └── use_cases/                   # Business logic
│       ├── get_current_weather.py
│       └── get_forecast.py
├── infrastructure/
│   └── external/
│       └── openweather_client.py    # OpenWeather API client
└── schemas/                         # Pydantic schemas for API I/O
    └── weather.py
```

### Kiến Trúc Chi Tiết

#### **1. API Layer** (`api/v1/`)

**Router** (`router.py`):
- Tổng hợp 2 endpoint groups: `/weather` và `/forecast`
- Prefix chung là `/api/v1`

**Endpoints**:
- `weather.py`: Endpoint lấy thời tiết hiện tại
- `forecast.py`: Endpoint lấy dự báo thời tiết
- Mỗi endpoint xử lý validation, error handling và gọi Use Cases

#### **2. Core Layer** (`core/`)

**Entity** (Domain model):
```python
@dataclass
class Weather:
    location: str
    temperature: float | None = None
    description: str | None = None
```

Đại diện cho thông tin thời tiết với 3 thuộc tính chính.

**Use Cases** (Business Logic):
- `GetCurrentWeather`: Use case đơn giản, chỉ ủy quyền cho client
- `GetForecast`: Use case đơn giản, chỉ ủy quyền cho client

**Đặc điểm**: Use cases trong service này rất thin, chỉ đóng vai trò điều phối (orchestration) giữa endpoint và infrastructure client. Business logic chủ yếu nằm ở việc mapping dữ liệu từ API response.

#### **3. Infrastructure Layer** (`infrastructure/`)

**OpenWeatherClient**:
- Gọi OpenWeatherMap API sử dụng `httpx.AsyncClient`
- Các phương thức chính:
  - `current_weather(location)`: Gọi `/weather` endpoint
  - `forecast(location)`: Gọi `/forecast` endpoint
- Map JSON response về `Weather` entities
- Xử lý timeout (10 seconds)
- Sử dụng `units=metric` để nhận temperature theo Celsius

**API Integration Details**:
```python
# Current weather
GET https://api.openweathermap.org/data/2.5/weather
    ?q={location}
    &appid={api_key}
    &units=metric

# Forecast
GET https://api.openweathermap.org/data/2.5/forecast
    ?q={location}
    &appid={api_key}
    &units=metric
```

#### **4. Schemas Layer** (`schemas/`)

**WeatherOut** (Pydantic model):
```python
class WeatherOut(BaseModel):
    location: str
    temperature: float | None = None
    description: str | None = None
```

Dùng cho API response validation và OpenAPI documentation.

### Đặc Điểm Thiết Kế

✅ **Stateless**: Không cache, mọi request gọi trực tiếp OpenWeather API  
✅ **Simple & Direct**: Use cases rất thin, logic chủ yếu ở infrastructure layer  
✅ **Async/Await**: Tất cả API calls đều async  
✅ **Error Handling**: Map HTTP errors từ OpenWeather thành meaningful exceptions  
✅ **Type Safety**: Sử dụng type hints và Pydantic models  

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

### **2. Thời Tiết Hiện Tại**

```http
GET /api/v1/weather/current?location={city_name}
```

**Query Parameters:**
- `location` (required): Tên thành phố hoặc địa điểm (e.g., "Paris", "Tokyo", "Hanoi")

**Response:** `200 OK`
```json
{
  "location": "Paris",
  "temperature": 15.5,
  "description": "scattered clouds"
}
```

**Errors:**
- `401`: OpenWeather unauthorized, check API key
- `500`: Missing OPENWEATHER_API_KEY
- `502`: OpenWeather API error (với status code cụ thể)

### **3. Dự Báo Thời Tiết**

```http
GET /api/v1/forecast?location={city_name}
```

**Query Parameters:**
- `location` (required): Tên thành phố hoặc địa điểm

**Response:** `200 OK`
```json
[
  {
    "location": "Paris",
    "temperature": 15.5,
    "description": "scattered clouds"
  },
  {
    "location": "Paris",
    "temperature": 14.2,
    "description": "light rain"
  },
  ...
]
```

**Note**: OpenWeather forecast API trả về dự báo 5 ngày với interval 3 giờ (tổng ~40 data points).

**Errors:**
- `401`: OpenWeather unauthorized, check API key
- `500`: Missing OPENWEATHER_API_KEY
- `502`: OpenWeather API error

---

## ⚙️ Giải Thích Hoạt Động

### **Flow 1: Lấy Thời Tiết Hiện Tại**

```
Client Request
    ↓
GET /api/v1/weather/current?location=Paris
    ↓
[weather.py:current_weather()]
    │
    ├─→ Kiểm tra OPENWEATHER_API_KEY
    │   (nếu thiếu → HTTPException 500)
    │
    ├─→ Khởi tạo OpenWeatherClient(api_key)
    │
    ├─→ Khởi tạo GetCurrentWeather use case
    │
    └─→ use_case.execute(location="Paris")
        ↓
    [get_current_weather.py:GetCurrentWeather.execute()]
        │
        └─→ return await self.client.current_weather(location)
            ↓
        [openweather_client.py:current_weather()]
            │
            ├─→ Prepare request
            │   url = "https://api.openweathermap.org/data/2.5/weather"
            │   params = {q: "Paris", appid: api_key, units: "metric"}
            │
            ├─→ httpx.AsyncClient.get(url, params)
            │   (timeout: 10s)
            │
            ├─→ response.raise_for_status()
            │   (nếu 401/404/5xx → httpx.HTTPStatusError)
            │
            ├─→ Parse JSON response
            │   data = response.json()
            │
            └─→ Map to Weather entity
                Weather(
                    location=data["name"] or location,
                    temperature=data["main"]["temp"],
                    description=data["weather"][0]["description"]
                )
                ↓
    Map to WeatherOut schema
    ↓
    Catch httpx.HTTPStatusError:
        ├─→ status 401 → HTTPException 401 "unauthorized"
        └─→ other → HTTPException 502 "OpenWeather error: {status}"
    ↓
JSON Response
```

**File liên quan:**
- `src/api/v1/endpoints/weather.py` (line 13-29)
- `src/core/use_cases/get_current_weather.py` (line 11-12)
- `src/infrastructure/external/openweather_client.py` (line 19-31)

**OpenWeather API Response Example:**
```json
{
  "name": "Paris",
  "main": {
    "temp": 15.5,
    "feels_like": 14.8,
    ...
  },
  "weather": [
    {
      "description": "scattered clouds",
      ...
    }
  ]
}
```

### **Flow 2: Lấy Dự Báo Thời Tiết**

```
GET /api/v1/forecast?location=Paris
    ↓
[forecast.py:forecast()]
    │
    ├─→ Kiểm tra OPENWEATHER_API_KEY
    ├─→ Khởi tạo OpenWeatherClient
    ├─→ Khởi tạo GetForecast use case
    │
    └─→ use_case.execute(location="Paris")
        ↓
    [get_forecast.py:GetForecast.execute()]
        │
        └─→ return await self.client.forecast(location)
            ↓
        [openweather_client.py:forecast()]
            │
            ├─→ Prepare request
            │   url = "https://api.openweathermap.org/data/2.5/forecast"
            │   params = {q: "Paris", appid: api_key, units: "metric"}
            │
            ├─→ httpx.AsyncClient.get(url, params)
            │
            ├─→ response.raise_for_status()
            │
            ├─→ Parse JSON response
            │   data = response.json()
            │   items = data["list"]  # Array of forecast data points
            │
            └─→ Loop through items and map to Weather entities
                for item in items:
                    Weather(
                        location=data["city"]["name"],
                        temperature=item["main"]["temp"],
                        description=item["weather"][0]["description"]
                    )
                ↓
    Map to list[WeatherOut]
    ↓
    Catch httpx.HTTPStatusError (similar to current weather)
    ↓
JSON Response (array)
```

**File liên quan:**
- `src/api/v1/endpoints/forecast.py` (line 13-29)
- `src/core/use_cases/get_forecast.py` (line 11-12)
- `src/infrastructure/external/openweather_client.py` (line 33-51)

**OpenWeather Forecast API Response Example:**
```json
{
  "city": {
    "name": "Paris"
  },
  "list": [
    {
      "main": {"temp": 15.5},
      "weather": [{"description": "scattered clouds"}]
    },
    {
      "main": {"temp": 14.2},
      "weather": [{"description": "light rain"}]
    },
    ...
  ]
}
```

### **Các Thành Phần Quan Trọng**

#### **OpenWeatherClient Implementation**

`src/infrastructure/external/openweather_client.py`:

**Constructor**:
```python
def __init__(self, api_key: str, base_url: str = "...", units: str = "metric"):
    self.api_key = api_key
    self.base_url = base_url.rstrip("/")
    self.units = units  # "metric" cho Celsius, "imperial" cho Fahrenheit
```

**Method `current_weather()`**:
- Gọi `/weather` endpoint với query params
- Parse response và extract: `name`, `main.temp`, `weather[0].description`
- Return single `Weather` entity

**Method `forecast()`**:
- Gọi `/forecast` endpoint
- Parse response và loop qua `list` array
- Extract: `city.name`, `main.temp`, `weather[0].description` cho mỗi item
- Return list of `Weather` entities

#### **Error Handling Strategy**

Tại endpoint layer (`weather.py`, `forecast.py`):

```python
try:
    weather = await use_case.execute(location)
except httpx.HTTPStatusError as exc:
    status = exc.response.status_code
    if status == 401:
        raise HTTPException(401, "OpenWeather unauthorized, check API key")
    raise HTTPException(502, f"OpenWeather error: {status}")
```

Chiến lược:
- Catch `httpx.HTTPStatusError` từ OpenWeather API
- Map 401 → client authentication error
- Map other errors → 502 Bad Gateway (upstream error)

#### **Settings Configuration**

`src/config/settings.py`:

```python
class Settings(BaseSettings):
    app_name: str = "weather-service"
    environment: str = "local"
    log_level: str = "INFO"
    redis_url: str = "redis://localhost:6379/0"  # Not used currently
    openweather_api_key: str | None = None       # Required!
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
APP_NAME=weather-service
ENVIRONMENT=local
LOG_LEVEL=INFO
REDIS_URL=redis://redis:6379/0
OPENWEATHER_API_KEY=your-openweather-api-key-here  # Bắt buộc!
```

Lấy API key tại: https://openweathermap.org/api

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
# Thời tiết hiện tại
curl "http://localhost:9000/api/v1/weather/current?location=Paris"

# Dự báo thời tiết
curl "http://localhost:9000/api/v1/weather/forecast?location=Tokyo"

# Response example
{
  "location": "Paris",
  "temperature": 15.5,
  "description": "scattered clouds"
}
```

**Lưu ý**: Middleware forward requests từ `/api/v1/weather/*` đến service này.

### **5. API Documentation**

Khi service đang chạy:

- **Swagger UI**: http://localhost:8000/docs (local)
- **ReDoc**: http://localhost:8000/redoc

Qua middleware: http://localhost:9000/docs

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

### **Lỗi: Missing OPENWEATHER_API_KEY**

```json
{
  "detail": "Missing OPENWEATHER_API_KEY"
}
```

**Giải pháp**: Thêm `OPENWEATHER_API_KEY` vào file `.env`

### **Lỗi: OpenWeather unauthorized (401)**

```json
{
  "detail": "OpenWeather unauthorized, check API key"
}
```

**Nguyên nhân**: API key không hợp lệ hoặc đã hết hạn

**Giải pháp**: 
- Verify API key tại https://openweathermap.org/api_keys
- Đảm bảo API key đã được activate (có thể mất vài giờ sau khi tạo mới)
- Kiểm tra quota limit của free tier

### **Lỗi: OpenWeather error (502)**

```json
{
  "detail": "OpenWeather error: 404"
}
```

**Nguyên nhân**: Địa điểm không tìm thấy hoặc OpenWeather API có vấn đề

**Giải pháp**: 
- Kiểm tra tên địa điểm có đúng không (e.g., "Paris", "London")
- Thử với location khác
- Kiểm tra OpenWeather API status: https://status.openweathermap.org/

### **Lỗi: Connection timeout**

**Nguyên nhân**: OpenWeather API chậm hoặc network issues

**Giải pháp**: 
- Kiểm tra internet connection
- Tăng timeout trong `OpenWeatherClient` (hiện tại 10s)
- Retry request

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

**Vai trò**: Cung cấp thông tin thời tiết hiện tại và dự báo cho các services khác (đặc biệt là itinerary planning).

---

## 📝 Notes

- Service **không cache dữ liệu**, mỗi request gọi trực tiếp OpenWeather API
- **Redis URL** được config nhưng chưa sử dụng (có thể implement caching sau)
- OpenWeather **free tier** có limit:
  - 60 calls/minute
  - 1,000,000 calls/month
- Temperature units: **metric** (Celsius) - có thể config thành imperial (Fahrenheit)
- Forecast data: **5 days, 3-hour intervals** (~40 data points)
- Use cases rất **thin layer**, chủ yếu là delegation pattern
- Service chạy trên **port 8000** internal, exposed qua middleware trên port 9000
- **Timeout**: 10 seconds cho mỗi OpenWeather API call

---

## 🎯 Future Improvements

1. **Caching**: Implement Redis caching để giảm API calls và tăng performance
2. **Rate Limiting**: Thêm rate limiting để tránh exceed OpenWeather quota
3. **Batch Requests**: Support multiple locations trong một request
4. **Extended Forecast**: Thêm endpoint cho hourly/daily aggregated forecast
5. **Weather Alerts**: Integrate weather alerts/warnings API
6. **Historical Data**: Thêm endpoint cho historical weather data
7. **Unit Tests**: Viết comprehensive unit tests với mocked OpenWeather responses
8. **Retry Logic**: Implement exponential backoff retry cho failed requests
