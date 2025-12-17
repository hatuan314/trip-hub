# Hướng dẫn sử dụng Flight Search Service

## 🎯 Tổng quan

Service tìm kiếm chuyến bay được xây dựng theo **MVC Pattern**:

- **Model (M)**: `src/core/entities/flight.py` - Định nghĩa các entity nghiệp vụ
- **View (V)**: `src/schemas/flight.py` - Schema request/response (Pydantic)
- **Controller (C)**: `src/api/v1/endpoints/flights.py` - Xử lý HTTP requests

## 🚀 Khởi động nhanh

### 1. Cài đặt dependencies

```bash
cd services/booking-service
source booking-venv/bin/activate
pip install -r requirements.txt
```

### 2. Chạy service

```bash
cd src
python main.py
```

Service sẽ chạy tại: http://localhost:8000

### 3. Truy cập API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 📡 API Examples

### Ví dụ 1: Tìm chuyến bay 1 chiều

```bash
curl -X POST "http://localhost:8000/api/v1/flights/search" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "HAN",
    "destination": "SGN",
    "departure_date": "2024-12-25",
    "adults": 1,
    "currency": "USD"
  }'
```

### Ví dụ 2: Tìm chuyến bay khứ hồi

```bash
curl -X POST "http://localhost:8000/api/v1/flights/search" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "HAN",
    "destination": "BKK",
    "departure_date": "2024-12-25",
    "return_date": "2024-12-30",
    "adults": 2,
    "travel_class": "ECONOMY",
    "non_stop": false,
    "currency": "USD",
    "max_results": 10
  }'
```

### Ví dụ 3: Tìm chuyến bay thẳng (non-stop)

```bash
curl -X POST "http://localhost:8000/api/v1/flights/search" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "SGN",
    "destination": "SIN",
    "departure_date": "2024-12-25",
    "adults": 1,
    "non_stop": true,
    "travel_class": "BUSINESS"
  }'
```

### Ví dụ 4: Tìm chuyến bay hạng thương gia

```bash
curl -X POST "http://localhost:8000/api/v1/flights/search" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "HAN",
    "destination": "NRT",
    "departure_date": "2024-12-25",
    "adults": 1,
    "travel_class": "BUSINESS",
    "currency": "USD"
  }'
```

## 🌍 IATA Codes phổ biến

### Việt Nam
- **HAN**: Nội Bài, Hà Nội
- **SGN**: Tân Sơn Nhất, TP.HCM
- **DAD**: Đà Nẵng
- **CXR**: Cam Ranh, Nha Trang
- **PQC**: Phú Quốc

### Đông Nam Á
- **BKK**: Bangkok, Thái Lan
- **SIN**: Singapore
- **KUL**: Kuala Lumpur, Malaysia
- **MNL**: Manila, Philippines
- **RGN**: Yangon, Myanmar

### Đông Á
- **NRT**: Tokyo Narita, Nhật Bản
- **HND**: Tokyo Haneda, Nhật Bản
- **ICN**: Seoul Incheon, Hàn Quốc
- **PEK**: Beijing, Trung Quốc
- **PVG**: Shanghai Pudong, Trung Quốc

## 📋 Tham số tìm kiếm

| Tham số | Bắt buộc | Mô tả | Ví dụ |
|---------|----------|-------|-------|
| `origin` | ✅ | Mã IATA sân bay xuất phát | "HAN" |
| `destination` | ✅ | Mã IATA sân bay đến | "BKK" |
| `departure_date` | ✅ | Ngày khởi hành (YYYY-MM-DD) | "2024-12-25" |
| `return_date` | ❌ | Ngày về (YYYY-MM-DD) | "2024-12-30" |
| `adults` | ❌ | Số hành khách (1-9) | 2 |
| `travel_class` | ❌ | Hạng vé | "ECONOMY", "BUSINESS" |
| `non_stop` | ❌ | Chỉ bay thẳng | true/false |
| `currency` | ❌ | Đơn vị tiền tệ | "USD", "VND" |
| `max_results` | ❌ | Số kết quả tối đa (1-250) | 10 |

## 🎓 Hạng vé (Travel Class)

- `ECONOMY`: Phổ thông
- `PREMIUM_ECONOMY`: Phổ thông đặc biệt
- `BUSINESS`: Thương gia
- `FIRST`: Hạng nhất

## 📊 Response Structure

```json
{
  "meta": {
    "count": 10
  },
  "data": [
    {
      "id": "1",
      "source": "GDS",
      "oneWay": false,
      "price": {
        "currency": "USD",
        "total": "250.00",
        "base": "200.00",
        "grandTotal": "250.00"
      },
      "itineraries": [
        {
          "duration": "PT2H30M",
          "segments": [
            {
              "departure": {
                "iataCode": "HAN",
                "at": "2024-12-25T10:00:00"
              },
              "arrival": {
                "iataCode": "BKK",
                "at": "2024-12-25T12:30:00"
              },
              "carrierCode": "VN",
              "number": "607",
              "aircraft": {
                "code": "321"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

## 🔍 Testing với Python

```python
import requests

url = "http://localhost:8000/api/v1/flights/search"
payload = {
    "origin": "HAN",
    "destination": "BKK",
    "departure_date": "2024-12-25",
    "adults": 1
}

response = requests.post(url, json=payload)
print(response.json())
```

## ⚠️ Lưu ý

1. **API Test Environment**: Đang sử dụng Amadeus Test API, có giới hạn số lượng request
2. **Date Format**: Ngày phải theo định dạng YYYY-MM-DD
3. **IATA Codes**: Phải là mã IATA hợp lệ (3 ký tự)
4. **Future Dates**: Ngày khởi hành phải là ngày trong tương lai

## 🐛 Troubleshooting

### Lỗi 401 Unauthorized
- Kiểm tra API Key và Secret trong `.env`
- Đảm bảo credentials còn hiệu lực

### Lỗi 400 Bad Request
- Kiểm tra format ngày (YYYY-MM-DD)
- Kiểm tra mã IATA có đúng không
- Kiểm tra số lượng hành khách (1-9)

### Lỗi 500 Internal Server Error
- Xem logs trong thư mục `logs/`
- Kiểm tra kết nối internet
- Kiểm tra Amadeus API có hoạt động không
