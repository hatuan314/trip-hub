# Trip Hub - Quick Start Guide 🚀

## TL;DR - Chạy Ngay trong 3 Phút

### Bước 1: Cấu Hình (1 phút)
```bash
cd services/booking-service
cp .env.example .env
```

Chỉnh sửa `.env` - **Thay thế API keys của bạn**:
```bash
AMADEUS_API_KEY=your_actual_key
AMADEUS_API_SECRET=your_actual_secret
```

### Bước 2: Khởi Động (2 phút)
```bash
# Về thư mục gốc
cd ../..

# Build và start tất cả services
docker-compose up --build -d
```

### Bước 3: Kiểm Tra
```bash
# Đợi ~30s để các services khởi động, sau đó:
curl http://localhost:9000/health
```

**Nếu thấy `{"status":"ok"}`** → ✅ **Thành công!**

---

## 🌐 Access Points

### Main Endpoint (Qua Middleware)
```
http://localhost:9000/api/v1/{service}/{path}
```

### Service Endpoints
| Service | Port | Health Check | API Docs |
|---------|------|--------------|----------|
| **Middleware** | 9000 | http://localhost:9000/health | http://localhost:9000/docs |
| Destination | 8001 | http://localhost:8001/health | http://localhost:8001/docs |
| Itinerary | 8002 | http://localhost:8002/health | - |
| Booking | 8003 | http://localhost:8003/health | http://localhost:8003/api/docs |
| Weather | 8004 | http://localhost:8004/health | http://localhost:8004/docs |

### Ví Dụ Request
```bash
# Qua Middleware (Khuyến nghị)
curl http://localhost:9000/api/v1/destination/destinations
curl http://localhost:9000/api/v1/weather/forecast
curl http://localhost:9000/api/v1/booking/flights/search
curl http://localhost:9000/api/v1/itinerary/plans

# Trực tiếp tới service
curl http://localhost:8001/api/v1/destinations
```

---

## 📊 Kiểm Tra Hệ Thống

### Check All Services
```bash
docker-compose ps
```

Expected output:
```
NAME                  STATUS
middleware-service    Up (healthy)
booking-service       Up (healthy)
destination-service   Up (healthy)
weather-service       Up (healthy)
itinerary-service     Up (healthy)
trip-hub-redis        Up (healthy)
```

### Xem Logs
```bash
# Tất cả services
docker-compose logs -f

# Một service cụ thể
docker-compose logs -f middleware-service
```

---

## 🛠️ Lệnh Thường Dùng

### Start/Stop
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild và start
docker-compose up --build -d
```

### Debugging
```bash
# Exec vào container
docker-compose exec middleware-service sh

# Xem logs real-time
docker-compose logs -f booking-service

# Check health
for port in 8001 8002 8003 8004 9000; do
  echo "Port $port:"
  curl -s http://localhost:$port/health | jq
done
```

### Clean Up
```bash
# Dừng và xóa containers
docker-compose down

# Xóa cả volumes (Redis data)
docker-compose down -v

# Xóa images
docker-compose down --rmi all

# Xóa tất cả (containers, volumes, images, networks)
docker-compose down -v --rmi all --remove-orphans
```

---

## ❗ Troubleshooting 5-Second Fix

### Problem: Container không start
```bash
docker-compose logs <service-name>
docker-compose up --build <service-name>
```

### Problem: Port conflict
```bash
# Tìm process đang dùng port
lsof -i :9000
# Kill nó hoặc đổi port trong docker-compose.yml
```

### Problem: Middleware 502 error
```bash
# Đợi cho tất cả services healthy
docker-compose ps
# Restart middleware
docker-compose restart middleware-service
```

### Problem: Amadeus API 401
```bash
# Kiểm tra .env
cat services/booking-service/.env
# Đảm bảo không có khoảng trắng: AMADEUS_API_KEY=abc123
```

---

## 🎯 Kiến Trúc Overview

```
Client → Middleware (9000)
           ├→ Destination (8001)
           ├→ Itinerary (8002)  
           ├→ Booking (8003) → Redis
           └→ Weather (8004)
```

**Middleware** là API Gateway - tất cả requests từ client đi qua đây!

---

## 📖 Tài Liệu Chi Tiết

Xem [DOCKER_DEPLOYMENT_GUIDE.md](./DOCKER_DEPLOYMENT_GUIDE.md) để biết:
- Kiến trúc chi tiết
- Cấu hình nâng cao
- Monitoring & logs
- Production deployment
- Troubleshooting đầy đủ

---

## 🆘 Còn Vấn Đề?

1. Check logs: `docker-compose logs -f`
2. Verify health: `curl http://localhost:9000/health`
3. Clean rebuild: `docker-compose down && docker-compose up --build`
4. Read full guide: [DOCKER_DEPLOYMENT_GUIDE.md](./DOCKER_DEPLOYMENT_GUIDE.md)

---

**Happy Coding! 🎉**
