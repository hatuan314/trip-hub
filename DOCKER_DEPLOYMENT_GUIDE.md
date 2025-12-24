# Trip Hub - Hướng Dẫn Triển Khai Docker

## 📋 Mục Lục
1. [Tổng Quan Kiến Trúc](#tổng-quan-kiến-trúc)
2. [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
3. [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
4. [Cài Đặt và Cấu Hình](#cài-đặt-và-cấu-hình)
5. [Chạy Hệ Thống](#chạy-hệ-thống)
6. [Kiểm Tra Hệ Thống](#kiểm-tra-hệ-thống)
7. [Quản Lý Services](#quản-lý-services)
8. [Troubleshooting](#troubleshooting)
9. [Monitoring và Logs](#monitoring-và-logs)

---

## 🏗️ Tổng Quan Kiến Trúc

### Kiến Trúc Microservices

Hệ thống Trip Hub được thiết kế theo mô hình **microservices** với các thành phần:

```
┌─────────────────────────────────────────────────────────┐
│                    Client / Browser                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP Requests
                     ▼
┌────────────────────────────────────────────────────────┐
│          Middleware Service (API Gateway)               │
│                  Port: 9000                             │
│          http://localhost:9000                          │
└─────┬──────────┬──────────┬──────────┬─────────────────┘
      │          │          │          │
      ▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Destination│ │ Weather  │ │ Booking  │ │Itinerary │
│  Service  │ │ Service  │ │ Service  │ │ Service  │
│Port: 8001 │ │Port: 8004│ │Port: 8003│ │Port: 8002│
└──────────┘ └──────────┘ └─────┬────┘ └──────────┘
                                │
                                ▼
                          ┌──────────┐
                          │  Redis   │
                          │Port: 6379│
                          └──────────┘
```

### Vai Trò Các Services

#### 1. **Middleware Service** (API Gateway)
- **Port**: 9000
- **Vai trò**: Điểm vào duy nhất cho client, routing requests tới các backend services
- **Endpoint**: `http://localhost:9000/api/v1/{service}/{path}`
- **Chức năng**: 
  - Request forwarding
  - Load balancing
  - API composition
  - Error handling

#### 2. **Destination Service**
- **Port**: 8001
- **Vai trò**: Quản lý thông tin điểm đến du lịch
- **Database**: SQLite/PostgreSQL (tùy cấu hình)
- **Endpoints**: `/api/v1/destinations/*`

#### 3. **Weather Service**
- **Port**: 8004
- **Vai trò**: Cung cấp thông tin thời tiết
- **Database**: SQLite/PostgreSQL
- **Endpoints**: `/api/v1/weather/*`

#### 4. **Booking Service**
- **Port**: 8003
- **Vai trò**: Quản lý đặt vé máy bay, khách sạn
- **Dependencies**: Redis (caching), Amadeus API
- **Endpoints**: `/api/v1/bookings/*`, `/api/v1/flights/*`, `/api/v1/hotels/*`

#### 5. **Itinerary Service**
- **Port**: 8002
- **Vai trò**: Quản lý lịch trình du lịch
- **Endpoints**: `/api/v1/itineraries/*`

#### 6. **Redis**
- **Port**: 6379
- **Vai trò**: Caching layer cho booking service
- **Persistence**: Volume-backed

---

## 💻 Yêu Cầu Hệ Thống

### Phần Mềm Cần Thiết

```bash
# Kiểm tra phiên bản
docker --version          # >= 20.10.0
docker-compose --version  # >= 2.0.0
```

### Yêu Cầu Tối Thiểu
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **RAM**: 4GB khả dụng
- **Disk**: 10GB trống
- **OS**: Linux, macOS, Windows (với WSL2)

### Cài Đặt Docker (nếu chưa có)

#### macOS
```bash
brew install docker docker-compose
# Hoặc tải Docker Desktop: https://www.docker.com/products/docker-desktop
```

#### Linux (Ubuntu/Debian)
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### Windows
- Tải và cài Docker Desktop: https://www.docker.com/products/docker-desktop
- Enable WSL2 backend

---

## 📁 Cấu Trúc Dự Án

```
trip-hub/
├── docker-compose.yml              # Main orchestration file
├── DOCKER_DEPLOYMENT_GUIDE.md      # Tài liệu này
│
├── services/
│   ├── middleware-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── src/
│   │
│   ├── destination-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── src/
│   │
│   ├── weather-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── src/
│   │
│   ├── booking-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env (cần tạo từ .env.example)
│   │   └── src/
│   │
│   └── itinerary-service/
│       ├── Dockerfile
│       ├── requirements.txt
│       └── src/
```

---

## ⚙️ Cài Đặt và Cấu Hình

### Bước 1: Clone Repository

```bash
cd /path/to/your/projects
git clone <repository-url>
cd trip-hub
```

### Bước 2: Cấu Hình Environment Variables

#### 2.1. Booking Service (BẮT BUỘC)
```bash
cd services/booking-service
cp .env.example .env
```

Chỉnh sửa file `.env`:
```bash
# API Keys - QUAN TRỌNG: Thay thế với keys thật của bạn
AMADEUS_API_KEY=your_actual_api_key_here
AMADEUS_API_SECRET=your_actual_api_secret_here

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL=3600

# App Configuration
APP_NAME=Booking Service
APP_VERSION=1.0.0
DEBUG=True
```

**Lấy Amadeus API Keys:**
1. Đăng ký tại: https://developers.amadeus.com/register
2. Tạo application mới
3. Copy API Key và API Secret

#### 2.2. Các Services Khác (Tùy chọn)

Các services khác sử dụng `.env.example` mặc định. Nếu cần tùy chỉnh:

```bash
# Destination Service
cd services/destination-service
cp .env.example .env

# Weather Service  
cd services/weather-service
cp .env.example .env

# Middleware Service
cd services/middleware-service
cp .env.example .env
```

### Bước 3: Xác Minh Cấu Hình

```bash
# Về thư mục gốc
cd /path/to/trip-hub

# Kiểm tra cấu trúc
ls -la services/*/Dockerfile
ls -la services/booking-service/.env

# Kiểm tra docker-compose config
docker-compose config
```

---

## 🚀 Chạy Hệ Thống

### Phương Pháp 1: Chạy Toàn Bộ Hệ Thống (Khuyến Nghị)

```bash
# Build và start tất cả services
docker-compose up --build

# Hoặc chạy ở chế độ background (detached)
docker-compose up --build -d
```

**Output mong đợi:**
```
✔ Container trip-hub-redis        Healthy
✔ Container destination-service   Healthy
✔ Container weather-service       Healthy  
✔ Container booking-service       Healthy
✔ Container itinerary-service     Healthy
✔ Container middleware-service    Started
```

### Phương Pháp 2: Chạy Từng Service

```bash
# Chỉ chạy destination service
docker-compose up destination-service

# Chạy middleware + dependencies
docker-compose up middleware-service
```

### Phương Pháp 3: Development Mode (với Hot Reload)

Chỉnh sửa `docker-compose.yml` để mount source code:

```yaml
# Thêm vào service cần develop
volumes:
  - ./services/destination-service/src:/app/src
```

Sau đó:
```bash
docker-compose up destination-service
```

---

## ✅ Kiểm Tra Hệ Thống

### 1. Kiểm Tra Container Status

```bash
# Xem tất cả containers
docker-compose ps

# Kiểm tra health status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**Output mong đợi:**
```
NAME                    STATUS
middleware-service      Up (healthy)
booking-service         Up (healthy)
destination-service     Up (healthy)
weather-service         Up (healthy)
itinerary-service       Up (healthy)
trip-hub-redis          Up (healthy)
```

### 2. Health Check Endpoints

```bash
# Health check cho từng service
curl http://localhost:8001/health  # Destination
curl http://localhost:8002/health  # Itinerary
curl http://localhost:8003/health  # Booking
curl http://localhost:8004/health  # Weather
curl http://localhost:9000/health  # Middleware

# Hoặc sử dụng script
for port in 8001 8002 8003 8004 9000; do
  echo "Checking port $port:"
  curl -s http://localhost:$port/health | jq
done
```

**Response mẫu:**
```json
{
  "status": "ok",
  "service": "destination-service"
}
```

### 3. Kiểm Tra API Documentation

Mở browser và truy cập:

```
# Middleware (API Gateway)
http://localhost:9000/docs

# Individual Services
http://localhost:8001/docs  # Destination
http://localhost:8002/docs  # Itinerary (nếu có)
http://localhost:8003/api/docs  # Booking
http://localhost:8004/docs  # Weather
```

### 4. Test API qua Middleware

```bash
# Test routing qua middleware
curl http://localhost:9000/api/v1/destination/destinations
curl http://localhost:9000/api/v1/weather/forecast
curl http://localhost:9000/api/v1/booking/flights/search
curl http://localhost:9000/api/v1/itinerary/plans
```

### 5. Kiểm Tra Redis

```bash
# Connect tới Redis container
docker exec -it trip-hub-redis redis-cli

# Trong redis-cli:
PING              # Should return PONG
KEYS *            # List all keys
INFO              # Redis info
EXIT
```

---

## 🔧 Quản Lý Services

### Xem Logs

```bash
# Xem logs tất cả services
docker-compose logs

# Xem logs real-time
docker-compose logs -f

# Xem logs một service cụ thể
docker-compose logs -f middleware-service
docker-compose logs -f booking-service

# Xem 100 dòng log cuối
docker-compose logs --tail=100 destination-service
```

### Restart Services

```bash
# Restart tất cả
docker-compose restart

# Restart một service
docker-compose restart middleware-service

# Rebuild và restart
docker-compose up --build -d middleware-service
```

### Stop/Start Services

```bash
# Stop tất cả (giữ containers)
docker-compose stop

# Stop một service
docker-compose stop booking-service

# Start lại
docker-compose start

# Stop và xóa containers
docker-compose down

# Stop, xóa containers và volumes
docker-compose down -v
```

### Scaling Services

```bash
# Scale destination service lên 3 instances
docker-compose up --scale destination-service=3 -d

# Kiểm tra
docker-compose ps destination-service
```

### Exec vào Container

```bash
# Mở shell trong container
docker-compose exec middleware-service sh
docker-compose exec booking-service bash

# Chạy lệnh trực tiếp
docker-compose exec booking-service python -m pip list
docker-compose exec destination-service ls -la /app
```

---

## 🔍 Troubleshooting

### Problem 1: Container không start

**Triệu chứng:**
```
Error: Container exited with code 1
```

**Giải pháp:**
```bash
# Xem logs chi tiết
docker-compose logs <service-name>

# Kiểm tra cấu hình
docker-compose config

# Rebuild clean
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Problem 2: Port đã được sử dụng

**Triệu chứng:**
```
Error: Bind for 0.0.0.0:8001 failed: port is already allocated
```

**Giải pháp:**
```bash
# Tìm process đang dùng port
lsof -i :8001
# hoặc
netstat -anv | grep 8001

# Kill process
kill -9 <PID>

# Hoặc thay đổi port trong docker-compose.yml
# Ví dụ: "8005:8000" thay vì "8001:8000"
```

### Problem 3: Middleware không kết nối được services

**Triệu chứng:**
```
502 Bad Gateway / Connection refused
```

**Giải pháp:**
```bash
# Kiểm tra network
docker network ls
docker network inspect trip-hub-network

# Kiểm tra tất cả services đã healthy
docker-compose ps

# Verify environment variables
docker-compose exec middleware-service env | grep SERVICE_URL

# Restart middleware sau khi services ready
docker-compose restart middleware-service
```

### Problem 4: Health check failed

**Triệu chứng:**
```
Container unhealthy
```

**Giải pháp:**
```bash
# Kiểm tra health endpoint bên trong container
docker-compose exec <service-name> curl http://localhost:8000/health

# Kiểm tra requests library đã cài đặt
docker-compose exec <service-name> python -c "import requests; print('OK')"

# Nếu thiếu requests, rebuild
docker-compose build --no-cache <service-name>
```

### Problem 5: Booking Service - Amadeus API Error

**Triệu chứng:**
```
401 Unauthorized / Invalid credentials
```

**Giải pháp:**
```bash
# Kiểm tra .env file
cat services/booking-service/.env

# Verify API keys không có khoảng trắng
AMADEUS_API_KEY=abc123  # ✓ Đúng
AMADEUS_API_KEY= abc123  # ✗ Sai (có space)

# Test API keys
docker-compose exec booking-service python -c "
from config.settings import get_settings
s = get_settings()
print(f'Key: {s.amadeus_api_key}')
print(f'Secret: {s.amadeus_api_secret}')
"
```

### Problem 6: Redis connection error

**Triệu chứng:**
```
Error connecting to Redis
```

**Giải pháp:**
```bash
# Kiểm tra Redis running
docker-compose ps redis

# Test connection
docker-compose exec booking-service python -c "
import redis
r = redis.Redis(host='redis', port=6379, db=0)
print(r.ping())
"

# Restart Redis
docker-compose restart redis
```

---

## 📊 Monitoring và Logs

### Log Files

Services tự động ghi logs ra stdout/stderr, được Docker capture:

```bash
# Export logs ra file
docker-compose logs > system-logs.txt
docker-compose logs booking-service > booking-logs.txt

# Logs với timestamp
docker-compose logs -t

# Follow logs từ thời điểm cụ thể
docker-compose logs --since 2024-01-01T10:00:00
docker-compose logs --since 30m
```

### Resource Usage

```bash
# Xem CPU, Memory, Network usage
docker stats

# Specific services
docker stats middleware-service booking-service

# Export metrics
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Network Inspection

```bash
# Inspect network
docker network inspect trip-hub-network

# Xem DNS resolution
docker-compose exec middleware-service nslookup destination-service
docker-compose exec middleware-service ping -c 2 booking-service
```

### Volume Inspection

```bash
# List volumes
docker volume ls

# Inspect Redis data volume
docker volume inspect trip-hub-redis-data

# Backup Redis data
docker run --rm -v trip-hub-redis-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/redis-backup-$(date +%Y%m%d).tar.gz -C /data .
```

---

## 🧪 Testing Workflow

### 1. Unit Testing (trong container)

```bash
# Nếu có tests
docker-compose exec destination-service pytest tests/
docker-compose exec booking-service python -m pytest
```

### 2. Integration Testing

```bash
# Test full flow qua middleware
curl -X POST http://localhost:9000/api/v1/destination/destinations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ha Noi",
    "description": "Capital of Vietnam"
  }'

# Verify response
curl http://localhost:9000/api/v1/destination/destinations
```

### 3. Load Testing

```bash
# Sử dụng Apache Bench
ab -n 1000 -c 10 http://localhost:9000/health

# Hoặc hey
hey -n 1000 -c 50 http://localhost:9000/api/v1/destination/destinations
```

---

## 🔐 Security Best Practices

### 1. Environment Variables
- ✅ **Luôn** sử dụng `.env` files, không hardcode
- ✅ Thêm `.env` vào `.gitignore`
- ✅ Sử dụng secrets management cho production

### 2. Network Isolation
- ✅ Services chỉ giao tiếp qua internal network
- ✅ Chỉ expose ports cần thiết ra host
- ✅ Middleware là điểm vào duy nhất

### 3. Container Security
```bash
# Scan images for vulnerabilities
docker scan middleware-service
docker scan booking-service

# Run as non-root user (thêm vào Dockerfile)
USER nobody
```

---

## 🚢 Production Deployment

### Docker Compose Production Override

Tạo file `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  middleware-service:
    restart: always
    environment:
      ENVIRONMENT: production
      LOG_LEVEL: WARNING
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

Chạy:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Environment-specific Configs

```bash
# Development
docker-compose up

# Staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 📚 Tài Liệu Tham Khảo

### Service-specific Documentation
- [Booking Service Guide](./services/booking-service/README.md)
- [Booking Service Docker](./services/booking-service/DOCKER.md)
- [Hotel Search Guide](./services/booking-service/HOTEL_SEARCH_GUIDE.md)

### External Resources
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Amadeus API](https://developers.amadeus.com/)

---

## ❓ FAQ

### Q: Làm sao để dừng tất cả và xóa sạch?
```bash
docker-compose down -v --remove-orphans
docker system prune -a --volumes
```

### Q: Thay đổi code có cần rebuild không?
- **Có volume mount**: Không cần, code tự động reload
- **Không có volume mount**: Có, chạy `docker-compose up --build`

### Q: Service nào cần internet?
- **Booking Service**: Cần kết nối Amadeus API
- **Các service khác**: Hoạt động offline được

### Q: Làm sao để debug?
```bash
# Add breakpoint trong code (nếu dùng debugpy)
# Set environment
DEBUG=True

# Attach debugger qua port 5678
```

---

## 🆘 Support

Nếu gặp vấn đề:

1. **Kiểm tra logs**: `docker-compose logs -f`
2. **Kiểm tra health**: `curl http://localhost:<port>/health`
3. **Rebuild clean**: `docker-compose down && docker-compose up --build`
4. **Tham khảo Troubleshooting section** ở trên

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Maintainer**: Trip Hub Development Team
