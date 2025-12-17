# Hướng dẫn sử dụng Hotel Search API

## 🎯 Tổng quan

API tìm kiếm khách sạn được xây dựng theo **MVC Pattern** sử dụng Amadeus Hotel Search API.

### Kiến trúc MVC:

- **Model (M)**: `src/core/entities/hotel.py` - Định nghĩa HotelEntity, Room, HotelAddress
- **View (V)**: `src/schemas/hotel.py` - Schema request/response (HotelSearchRequest, HotelSearchResponse)
- **Controller (C)**: `src/api/v1/endpoints/hotels.py` - Xử lý HTTP requests

## 📡 API Endpoints

### 1. Tìm kiếm khách sạn theo thành phố

**POST** `/api/v1/hotels/search`

**Trường bắt buộc:**
- `city_code` - Mã IATA của thành phố (3 ký tự)
- `check_in_date` - Ngày nhận phòng (YYYY-MM-DD)
- `check_out_date` - Ngày trả phòng (YYYY-MM-DD)
- `adults` - Số người lớn (1-9)

**Trường tùy chọn:**
- `children` - Số trẻ em (0-9)
- `rooms` - Số phòng (1-9)
- `radius` - Bán kính tìm kiếm (km)
- `currency` - Đơn vị tiền tệ
- `payment_policy` - Chính sách thanh toán
- `board_type` - Loại bữa ăn
- `max_results` - Số kết quả tối đa

**Request Body:**
```json
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

**Response:**
```json
{
  "data": [
    {
      "type": "hotel-offers",
      "hotel": {
        "hotelId": "BKXXX001",
        "name": "Grand Hotel Bangkok",
        "rating": "5",
        "cityCode": "BKK",
        "latitude": 13.7563,
        "longitude": 100.5018
      },
      "available": true,
      "offers": [
        {
          "id": "OFFER123",
          "checkInDate": "2025-02-01",
          "checkOutDate": "2025-02-05",
          "room": {
            "type": "DELUXE_ROOM",
            "description": {
              "text": "Deluxe Room with City View"
            }
          },
          "guests": {
            "adults": 2
          },
          "price": {
            "currency": "USD",
            "base": "120.00",
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

### 2. Lấy chi tiết khách sạn và giá phòng

**POST** `/api/v1/hotels/offers`

**Request Body:**
```json
{
  "hotel_id": "BKXXX001",
  "check_in_date": "2025-02-01",
  "check_out_date": "2025-02-05",
  "adults": 2,
  "rooms": 1,
  "currency": "USD"
}
```

## 🧪 Ví dụ sử dụng

### Ví dụ 1: Tìm khách sạn ở Bangkok

```bash
curl -X POST "http://localhost:8000/api/v1/hotels/search" \
  -H "Content-Type: application/json" \
  -d '{
    "city_code": "BKK",
    "check_in_date": "2025-02-01",
    "check_out_date": "2025-02-05",
    "adults": 2,
    "children": 0,
    "rooms": 1,
    "currency": "USD"
  }'
```

### Ví dụ 2: Tìm khách sạn ở Singapore cho gia đình

```bash
curl -X POST "http://localhost:8000/api/v1/hotels/search" \
  -H "Content-Type: application/json" \
  -d '{
    "city_code": "SIN",
    "check_in_date": "2025-03-10",
    "check_out_date": "2025-03-15",
    "adults": 2,
    "children": 2,
    "rooms": 2,
    "radius": 5,
    "currency": "USD",
    "board_type": "BREAKFAST"
  }'
```

### Ví dụ 3: Tìm khách sạn ở Paris

```bash
curl -X POST "http://localhost:8000/api/v1/hotels/search" \
  -H "Content-Type: application/json" \
  -d '{
    "city_code": "PAR",
    "check_in_date": "2025-04-01",
    "check_out_date": "2025-04-07",
    "adults": 2,
    "rooms": 1,
    "radius": 10,
    "currency": "EUR",
    "max_results": 20
  }'
```

### Ví dụ 4: Lấy chi tiết khách sạn cụ thể

```bash
curl -X POST "http://localhost:8000/api/v1/hotels/offers" \
  -H "Content-Type: application/json" \
  -d '{
    "hotel_id": "BKXXX001",
    "check_in_date": "2025-02-01",
    "check_out_date": "2025-02-05",
    "adults": 2,
    "rooms": 1,
    "currency": "USD"
  }'
```

## 🌍 Mã IATA thành phố phổ biến

### Châu Á
- **BKK** - Bangkok, Thái Lan
- **SIN** - Singapore
- **HKG** - Hong Kong
- **TYO** - Tokyo, Nhật Bản
- **SEL** - Seoul, Hàn Quốc
- **BOM** - Mumbai, Ấn Độ
- **DEL** - Delhi, Ấn Độ
- **DXB** - Dubai, UAE
- **KUL** - Kuala Lumpur, Malaysia
- **MNL** - Manila, Philippines

### Châu Âu
- **LON** - London, Anh
- **PAR** - Paris, Pháp
- **ROM** - Rome, Ý
- **BCN** - Barcelona, Tây Ban Nha
- **BER** - Berlin, Đức
- **AMS** - Amsterdam, Hà Lan
- **VIE** - Vienna, Áo
- **PRG** - Prague, Séc

### Châu Mỹ
- **NYC** - New York, Mỹ
- **LAX** - Los Angeles, Mỹ
- **MIA** - Miami, Mỹ
- **YTO** - Toronto, Canada
- **MEX** - Mexico City, Mexico

## 📋 Tham số chi tiết

### Payment Policy
- `GUARANTEE` - Đảm bảo thanh toán
- `DEPOSIT` - Đặt cọc
- `NONE` - Không yêu cầu

### Board Type (Loại bữa ăn)
- `ROOM_ONLY` - Chỉ phòng
- `BREAKFAST` - Bao gồm bữa sáng
- `HALF_BOARD` - Nửa suất (sáng + tối)
- `FULL_BOARD` - Đầy đủ (sáng + trưa + tối)
- `ALL_INCLUSIVE` - Tất cả bao gồm

### Radius Unit
- `KM` - Kilômét
- `MILE` - Dặm

## 🔍 Testing với Python

```python
import requests

url = "http://localhost:8000/api/v1/hotels/search"
payload = {
    "city_code": "BKK",
    "check_in_date": "2025-02-01",
    "check_out_date": "2025-02-05",
    "adults": 2,
    "children": 1,
    "rooms": 1,
    "currency": "USD"
}

response = requests.post(url, json=payload)
print(response.json())
```

## ⚠️ Lưu ý

1. **Ngày tháng**: 
   - Ngày nhận phòng phải là ngày trong tương lai
   - Ngày trả phòng phải sau ngày nhận phòng
   - Format: YYYY-MM-DD

2. **Mã thành phố**:
   - Phải là mã IATA hợp lệ (3 ký tự)
   - Viết hoa hoặc thường đều được

3. **Số người**:
   - Adults: 1-9 người
   - Children: 0-9 trẻ
   - Rooms: 1-9 phòng

4. **API Limits**:
   - Đang sử dụng Amadeus Test API
   - Có giới hạn số lượng request
   - Một số khách sạn có thể không có sẵn phòng

## 🐛 Troubleshooting

### Lỗi 400 - Bad Request
- Kiểm tra format ngày tháng
- Kiểm tra mã thành phố có đúng không
- Đảm bảo số người hợp lệ

### Lỗi 404 - Not Found
- Hotel ID không tồn tại
- Thử tìm kiếm lại để lấy hotel ID mới

### Lỗi 500 - Internal Server Error
- Kiểm tra logs trong `logs/booking-service.log`
- Kiểm tra kết nối internet
- Kiểm tra Amadeus API credentials

## 📚 Tài liệu tham khảo

- Amadeus Hotel Search API: https://developers.amadeus.com/self-service/category/hotels
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
