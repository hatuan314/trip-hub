# Middleware Service

Service FastAPI đóng vai trò lớp middleware/gateway nhận yêu cầu từ client và phân chia tới đúng microservice (destination, weather). Request được forward giữ nguyên method, query, headers; lỗi downstream sẽ trả về 5xx phù hợp.

## Cách hoạt động nhanh
- Đường dẫn nhận: `/api/v1/{service}/{path...}` với `service` ∈ `destination | weather`.
- Ví dụ: `GET /api/v1/destination/destinations?query=paris` → proxy tới `DESTINATION_SERVICE_URL/api/v1/destinations?query=paris`.
- Health check: `GET /health` trả về danh sách service đang cấu hình.

## Chạy cục bộ
```bash
cd services/middleware-service
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Điều chỉnh URL từng downstream service nếu cần
uvicorn src.main:app --reload --port 9000
```

Tùy chỉnh `.env`:
- `DESTINATION_SERVICE_URL`, `WEATHER_SERVICE_URL`: base URL các service downstream (mặc định ví dụ trên các port tách biệt 8001/8004).
- `API_PREFIX`: prefix chung cho cả middleware và downstream (mặc định `/api/v1`).
- `HTTP_TIMEOUT`: timeout cho request tới downstream (giây).
