# Hướng Dẫn Triển Khai Hệ Thống Microservice

## Tổng Quan Kiến Trúc

Hệ thống travel-planning-app được thiết kế theo chuẩn **microservice architecture** với các thành phần:

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network (trip-network)            │
│                                                             │
│  ┌──────────────────┐                                      │
│  │   middleware     │ ← Port 9000 (Public API Gateway)     │
│  │   service        │                                       │
│  └────────┬─────────┘                                      │
│           │                                                 │
│           ├──────────┬──────────┬──────────┬──────────┐   │
│           ↓          ↓          ↓          ↓          ↓   │
│  ┌────────────┐ ┌────────┐ ┌─────────┐ ┌─────────┐      │
│  │destination │ │weather │ │itinerary│ │ booking │      │
│  │  service   │ │service │ │ service │ │ service │      │
│  └────────────┘ └───┬────┘ └─────────┘ └────┬────┘      │
│                     │                        │            │
│                     ↓                        ↓            │
│              ┌──────────┐              ┌─────────┐       │
│              │PostgreSQL│              │  Redis  │       │
│              └──────────┘              └─────────┘       │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

## Services và Chức Năng

### 1. **Middleware Service** (API Gateway)
- **Port**: 9000 (external)
- **Vai trò**: API Gateway, authentication, request routing
- **Endpoints**: `/api/v1/{service}/{path}`
- **Routes to**: destination, weather, itinerary, booking

### 2. **Destination Service**
- **Port**: 8000 (internal only)
- **Chức năng**: Quản lý thông tin điểm đến du lịch
- **Dependencies**: None

### 3. **Weather Service**
- **Port**: 8000 (internal only)
- **Chức năng**: Thông tin thời tiết
- **Dependencies**: PostgreSQL, Redis
- **External API**: OpenWeather API

### 4. **Itinerary Service**
- **Port**: 8000 (internal only)
- **Chức năng**: Lập lịch trình du lịch
- **Dependencies**: None

### 5. **Booking Service**
- **Port**: 8000 (internal only)
- **Chức năng**: Đặt vé máy bay và khách sạn
- **Dependencies**: Redis
- **External API**: Amadeus API

### 6. **Infrastructure Services**
- **Redis**: Cache cho booking và weather services
- **PostgreSQL**: Database cho weather service

## Yêu Cầu Hệ Thống

- Docker Engine 20.10+
- Docker Compose 2.0+
- Minimum RAM: 4GB
- Disk space: 5GB

## Cấu Hình Environment Variables

### 1. Middleware Service
```bash
# services/middleware-service/.env
APP_NAME=middleware-service
ENVIRONMENT=local
LOG_LEVEL=INFO
API_PREFIX=/api/v1
HTTP_TIMEOUT=10

DESTINATION_SERVICE_URL=http://destination-service:8000
WEATHER_SERVICE_URL=http://weather-service:8000
ITINERARY_SERVICE_URL=http://itinerary-service:8000
BOOKING_SERVICE_URL=http://booking-service:8000
```

### 2. Booking Service
```bash
# services/booking-service/.env
APP_NAME=Booking Service
APP_VERSION=1.0.0
DEBUG=True

AMADEUS_API_KEY=your-api-key-here
AMADEUS_API_SECRET=your-api-secret-here
AMADEUS_BASE_URL=https://test.api.amadeus.com

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL=3600
```

### 3. Weather Service
```bash
# services/weather-service/.env
APP_NAME=weather-service
ENVIRONMENT=local
LOG_LEVEL=INFO
DATABASE_URL=postgresql+psycopg2://user:password@postgres:5432/app
REDIS_URL=redis://redis:6379/0
OPENWEATHER_API_KEY=your-openweather-key
```

### 4. Destination Service
```bash
# services/destination-service/.env
# Copy from .env.example
```

## Triển Khai

### Step 1: Cấu Hình Environment
```bash
# Copy và chỉnh sửa env files
cp services/booking-service/.env.example services/booking-service/.env
cp services/weather-service/.env.example services/weather-service/.env
cp services/destination-service/.env.example services/destination-service/.env
cp services/middleware-service/.env.example services/middleware-service/.env

# Cập nhật API keys trong các file .env
# - AMADEUS_API_KEY và AMADEUS_API_SECRET trong booking-service/.env
# - OPENWEATHER_API_KEY trong weather-service/.env
```

### Step 2: Build và Start Services
```bash
# Build tất cả services
docker-compose build

# Start hệ thống
docker-compose up -d

# Xem logs
docker-compose logs -f

# Xem logs của 1 service cụ thể
docker-compose logs -f middleware-service
```

### Step 3: Kiểm Tra Health Status
```bash
# Check middleware service (API Gateway)
curl http://localhost:9000/health

# Expected response:
# {
#   "status": "ok",
#   "service": "middleware-service",
#   "forwarding_to": ["booking", "destination", "itinerary", "weather"]
# }

# Kiểm tra tất cả services thông qua middleware
curl http://localhost:9000/api/v1/destination/...
curl http://localhost:9000/api/v1/weather/...
curl http://localhost:9000/api/v1/itinerary/...
curl http://localhost:9000/api/v1/booking/...
```

### Step 4: Xem Container Status
```bash
# Xem tất cả containers
docker-compose ps

# Expected output:
# NAME                      STATUS        PORTS
# trip-middleware-service   Up (healthy)  0.0.0.0:9000->8000/tcp
# trip-booking-service      Up (healthy)
# trip-destination-service  Up (healthy)
# trip-weather-service      Up (healthy)
# trip-itinerary-service    Up (healthy)
# trip-redis                Up (healthy)
# trip-postgres             Up (healthy)
```

## Cơ Chế Docker Network

### Service Discovery với Docker DNS
Các services giao tiếp với nhau qua **Docker DNS** trong network `trip-network`:

```python
# Middleware service gọi destination service
response = await client.request(
    url="http://destination-service:8000/api/v1/destinations"
    # Docker tự động resolve "destination-service" -> 172.18.0.X
)
```

### Network Isolation
- **Internal services**: Chỉ giao tiếp trong Docker network
- **External access**: Chỉ qua middleware-service (port 9000)
- **Security**: Services không expose ports ra ngoài

## Health Checks

Tất cả services đều có health check endpoints:
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3 lần
- **Start period**: 40 seconds (cho services khởi động)

Docker sẽ tự động restart containers nếu health check fail.

## Troubleshooting

### Services không start được
```bash
# Xem logs chi tiết
docker-compose logs service-name

# Rebuild từ đầu
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Connection refused giữa các services
```bash
# Kiểm tra network
docker network inspect trip-network

# Verify DNS resolution
docker exec trip-middleware-service nslookup destination-service
```

### Database connection issues
```bash
# Kiểm tra PostgreSQL
docker exec trip-postgres pg_isready -U user

# Kiểm tra Redis
docker exec trip-redis redis-cli ping
```

## Scaling Services

```bash
# Scale một service cụ thể
docker-compose up -d --scale destination-service=3

# Lưu ý: Cần thêm load balancer cho production
```

## Dừng Hệ Thống

```bash
# Dừng services (giữ data)
docker-compose stop

# Dừng và xóa containers (giữ volumes)
docker-compose down

# Xóa hoàn toàn (bao gồm volumes)
docker-compose down -v
```

## Production Considerations

### 1. Environment Variables
- Sử dụng secrets management (e.g., Docker Secrets, HashiCorp Vault)
- Không commit API keys vào git

### 2. Logging
- Tích hợp centralized logging (ELK Stack, Loki)
- Log aggregation qua Docker logging drivers

### 3. Monitoring
- Thêm Prometheus + Grafana
- Health check monitoring
- Resource usage tracking

### 4. Security
- HTTPS cho external traffic
- API rate limiting
- Authentication/Authorization
- Network policies

### 5. High Availability
- Load balancer cho middleware service
- Multi-replica deployment
- Database replication
- Redis cluster

## API Documentation

Sau khi start services, truy cập Swagger docs:
- **Middleware**: http://localhost:9000/docs
- **Services**: Không expose trực tiếp (chỉ qua middleware)

## Architecture Benefits

✅ **Độc lập**: Mỗi service có lifecycle riêng
✅ **Scalable**: Scale từng service độc lập
✅ **Resilient**: Service failure không ảnh hưởng toàn hệ thống
✅ **Maintainable**: Code base nhỏ, dễ maintain
✅ **Technology agnostic**: Có thể dùng tech stack khác nhau
✅ **Deployment**: Deploy từng service độc lập

## Monitoring Commands

```bash
# Xem resource usage
docker stats

# Xem network traffic
docker network inspect trip-network

# Xem volumes
docker volume ls

# Backup Redis data
docker exec trip-redis redis-cli BGSAVE

# Backup PostgreSQL
docker exec trip-postgres pg_dump -U user app > backup.sql
```
