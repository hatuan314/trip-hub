# Booking Service - Flight Search

Service tìm kiếm chuyến bay sử dụng Amadeus API theo MVC Pattern.

## 🏗️ Kiến trúc MVC

### Model (M)
- **Location**: `src/core/entities/flight.py`
- **Mô tả**: Định nghĩa các entity như FlightEntity, Airport, Segment, Price
- **Chức năng**: Đại diện cho dữ liệu nghiệp vụ của chuyến bay

### View (V)
- **Location**: `src/schemas/flight.py`
- **Mô tả**: Định nghĩa các schema Pydantic cho request/response
- **Chức năng**: Validate input và format output (FlightSearchRequest, FlightSearchResponse)

### Controller (C)
- **Location**: `src/api/v1/endpoints/flights.py`
- **Mô tả**: Xử lý HTTP requests và điều phối logic
- **Chức năng**: Nhận request, gọi use case, trả về response

### Business Logic
- **Location**: `src/core/use_cases/search_flights.py`
- **Mô tả**: Chứa logic nghiệp vụ tìm kiếm chuyến bay
- **Chức năng**: Orchestrate giữa controller và external API

### External Integration
- **Location**: `src/infrastructure/external/amadeus_client.py`
- **Mô tả**: Client tích hợp với Amadeus API
- **Chức năng**: Xác thực và gọi API Amadeus

## 🚀 Cài đặt

### 1. Tạo môi trường ảo
```bash
cd services/booking-service
python3 -m venv booking-venv
source booking-venv/bin/activate  # macOS/Linux
# hoặc
booking-venv\Scripts\activate  # Windows
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình môi trường
```bash
cp .env.example .env
# Chỉnh sửa .env nếu cần
```

### 4. Chạy service
```bash
# Chạy từ thư mục src
cd src
python main.py
```

Hoặc sử dụng uvicorn (khuyến nghị):
```bash
# Chạy từ thư mục gốc booking-service
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### Flight Search (Tìm kiếm chuyến bay)

#### 1. Tìm kiếm chuyến bay
**POST** `/api/v1/flights/search`

**Request Body:**
```json
{
  "origin": "HAN",
  "destination": "BKK",
  "departure_date": "2024-12-25",
  "return_date": "2024-12-30",
  "adults": 2,
  "travel_class": "ECONOMY",
  "non_stop": false,
  "currency": "USD",
  "max_results": 10
}
```

**Response:**
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

#### 2. Lấy chi tiết chuyến bay
**GET** `/api/v1/flights/{offer_id}`

#### 3. Health check
**GET** `/api/v1/flights/health`

### Hotel Search (Tìm kiếm khách sạn)

#### 1. Tìm kiếm khách sạn theo thành phố
**POST** `/api/v1/hotels/search`

**Request Body:**
```json
{
  "city_code": "BKK",
  "check_in_date": "2025-02-01",
  "check_out_date": "2025-02-05",
  "adults": 2,
  "children": 1,
  "rooms": 1,
  "currency": "USD"
}
```

**Response:**
```json
{
  "data": [
    {
      "hotel": {
        "hotelId": "BKXXX001",
        "name": "Grand Hotel Bangkok",
        "rating": "5"
      },
      "offers": [
        {
          "price": {
            "currency": "USD",
            "total": "150.00"
          }
        }
      ]
    }
  ]
}
```

#### 2. Lấy chi tiết khách sạn
**POST** `/api/v1/hotels/offers`

#### 3. Health check
**GET** `/api/v1/hotels/health`

## 🧪 Test API

### Test Flight Search
```bash
curl -X POST "http://localhost:8000/api/v1/flights/search" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "HAN",
    "destination": "BKK",
    "departure_date": "2025-01-15",
    "return_date": "2025-01-20",
    "adults": 2,
    "currency": "USD"
  }'
```

### Test Hotel Search
```bash
curl -X POST "http://localhost:8000/api/v1/hotels/search" \
  -H "Content-Type: application/json" \
  -d '{
    "city_code": "BKK",
    "check_in_date": "2025-02-01",
    "check_out_date": "2025-02-05",
    "adults": 2,
    "children": 1,
    "rooms": 1,
    "currency": "USD"
  }'
```

### Sử dụng Swagger UI
Truy cập: http://localhost:8000/api/docs

## 📁 Cấu trúc thư mục

```
booking-service/
├── src/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── flights.py          # Controller
│   │       └── router.py
│   ├── core/
│   │   ├── entities/
│   │   │   └── flight.py               # Model (Entity)
│   │   └── use_cases/
│   │       └── search_flights.py       # Business Logic
│   ├── infrastructure/
│   │   └── external/
│   │       └── amadeus_client.py       # External API Client
│   ├── schemas/
│   │   └── flight.py                   # View (Request/Response)
│   ├── config/
│   │   ├── settings.py
│   │   └── logging.py
│   └── main.py                         # FastAPI Application
├── requirements.txt
├── .env.example
└── README.md
```

## 🔑 Amadeus API

### API Credentials
- **API Key**: vufTw1626D0b6oBAOc4imErAWpvEGVFR
- **API Secret**: dCILSPjIHv40Hyfg
- **Environment**: Test (https://test.api.amadeus.com)

### Supported APIs
1. **Flight Offers Search** - Tìm kiếm chuyến bay
2. **Hotel Search** - Tìm kiếm khách sạn theo thành phố

### IATA Codes (Ví dụ)

**Sân bay:**
- **HAN**: Nội Bài, Hà Nội
- **SGN**: Tân Sơn Nhất, TP.HCM
- **BKK**: Suvarnabhumi, Bangkok
- **SIN**: Changi, Singapore
- **NRT**: Narita, Tokyo

**Thành phố (cho hotel search):**
- **BKK**: Bangkok, Thái Lan
- **SIN**: Singapore
- **PAR**: Paris, Pháp
- **LON**: London, Anh
- **NYC**: New York, Mỹ

## 📝 Ghi chú

- Service sử dụng Amadeus Test API (miễn phí nhưng có giới hạn)
- Access token tự động refresh khi hết hạn
- Logs được lưu trong thư mục `logs/`
- CORS được bật cho phép test từ frontend
- Hỗ trợ 2 tính năng chính:
  - ✈️ **Flight Search**: Tìm kiếm chuyến bay giữa 2 địa điểm
  - 🏨 **Hotel Search**: Tìm kiếm khách sạn theo thành phố

## 🛠️ Development

### Thêm endpoint mới
1. Tạo schema trong `src/schemas/`
2. Tạo entity trong `src/core/entities/`
3. Tạo use case trong `src/core/use_cases/`
4. Tạo endpoint trong `src/api/v1/endpoints/`
5. Register router trong `src/api/v1/router.py`

### Best Practices
- Luôn validate input với Pydantic schemas
- Xử lý exceptions và log errors
- Sử dụng dependency injection cho use cases
- Tách biệt business logic khỏi HTTP layer

## 📚 Documentation

- **Flight Search Guide**: Xem `README.md` (phần này)
- **Hotel Search Guide**: Xem `HOTEL_SEARCH_GUIDE.md`
- **Usage Examples**: Xem `USAGE.md`
- **API Documentation**: http://localhost:8000/api/docs
