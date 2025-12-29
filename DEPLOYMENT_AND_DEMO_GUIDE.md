# Hướng Dẫn Triển Khai và Demo Hệ Thống Trip Hub

**Tài liệu này hướng dẫn chi tiết cách triển khai hệ thống Trip Hub microservices trên Docker và chạy demo qua Web UI.**

---

## 📋 Mục Lục

1. [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
2. [Tổng Quan Kiến Trúc](#tổng-quan-kiến-trúc)
3. [Cài Đặt và Cấu Hình](#cài-đặt-và-cấu-hình)
4. [Triển Khai với Docker](#triển-khai-với-docker)
5. [Chạy Web Demo](#chạy-web-demo)
6. [Hướng Dẫn Sử Dụng](#hướng-dẫn-sử-dụng)
7. [Troubleshooting](#troubleshooting)

---

## 🖥️ Yêu Cầu Hệ Thống

### **Phần Mềm**
- **Docker Engine**: 20.10+ ([Cài đặt Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: 2.0+ (đi kèm với Docker Desktop)
- **Python**: 3.8+ (cho web server local - optional)
- **Web Browser**: Chrome, Firefox, Edge, Safari (bất kỳ)

### **Phần Cứng**
- **RAM**: Tối thiểu 4GB (khuyến nghị 8GB)
- **Disk**: 5GB trống
- **CPU**: 2 cores trở lên

### **Mạng**
- Kết nối internet (để pull Docker images và gọi external APIs)
- Ports available: 9000 (API Gateway), 8080 (Web UI)

---

## 🏗️ Tổng Quan Kiến Trúc

### **System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Network                          │
│                      (trip-network)                          │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │          Middleware Service                   │          │
│  │          (API Gateway)                        │          │
│  │          Port: 9000 ← Public Access          │          │
│  └────────┬─────────┬─────────┬──────────┬──────┘          │
│           │         │         │          │                  │
│           ↓         ↓         ↓          ↓                  │
│  ┌─────────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐    │
│  │Destination │ │Weather  │ │Itinerary│ │ Booking  │    │
│  │ Service    │ │Service  │ │Service  │ │ Service  │    │
│  │  (8001)    │ │ (8002)  │ │ (8000)  │ │  (8000)  │    │
│  └──────┬──────┘ └────┬────┘ └────┬────┘ └────┬─────┘    │
│         │             │            │            │          │
│         ↓             ↓            ↓            ↓          │
│    ┌────────┐   ┌──────────┐  ┌──────────┐ ┌──────┐     │
│    │ MySQL  │   │PostgreSQL│  │PostgreSQL│ │Redis │     │
│    │        │   │          │  │ (shared) │ │      │     │
│    └────────┘   └──────────┘  └──────────┘ └──────┘     │
│                                                            │
└────────────────────────────────────────────────────────────┘
          ↑
          │ HTTP Requests
          │
    ┌─────────────┐
    │   Web UI    │
    │ (Port 8080) │
    └─────────────┘
```

### **Services Overview**

| Service | Port | Database | External API | Chức Năng |
|---------|------|----------|--------------|-----------|
| **Middleware** | 9000 | PostgreSQL | - | API Gateway, Auth |
| **Destination** | 8001 | MySQL | - | Điểm đến du lịch |
| **Weather** | 8002 | PostgreSQL | OpenWeatherMap | Thời tiết |
| **Booking** | 8000 | Redis | Amadeus | Flights/Hotels |
| **Itinerary** | 8000 | PostgreSQL | - | Lịch trình |

---

## ⚙️ Cài Đặt và Cấu Hình

### **Step 1: Clone Repository**

```bash
# Clone project
git clone <repository-url>
cd trip-hub

# Verify structure
ls -la
# Expected: docker-compose.yml, services/, web/, docs/
```

### **Step 2: Cấu Hình Environment Variables**

Mỗi service cần file `.env` để lưu cấu hình.

#### **2.1 Middleware Service**

```bash
cd services/middleware-service
cp .env.example .env
```

Nội dung `.env`:
```bash
APP_NAME=middleware-service
ENVIRONMENT=local
LOG_LEVEL=INFO
API_PREFIX=/api/v1
HTTP_TIMEOUT=10

# Database (shared với itinerary-service)
DATABASE_URL=postgresql+psycopg2://trip:trip@postgres:5432/trip_hub

# Downstream service URLs (Docker DNS)
DESTINATION_SERVICE_URL=http://destination-service:8001
WEATHER_SERVICE_URL=http://weather-service:8002
ITINERARY_SERVICE_URL=http://itinerary-service:8000
BOOKING_SERVICE_URL=http://booking-service:8000
```

#### **2.2 Booking Service**

```bash
cd ../booking-service
cp .env.example .env
```

Nội dung `.env`:
```bash
APP_NAME=Booking Service
APP_VERSION=1.0.0
DEBUG=True

# Amadeus API (Test environment)
AMADEUS_API_KEY=vufTw1626D0b6oBAOc4imErAWpvEGVFR
AMADEUS_API_SECRET=dCILSPjIHv40Hyfg
AMADEUS_BASE_URL=https://test.api.amadeus.com

# Redis cache
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL=3600
```

⚠️ **Note**: Amadeus credentials trên là test API keys. Có thể tạo account riêng tại [developers.amadeus.com](https://developers.amadeus.com)

#### **2.3 Weather Service**

```bash
cd ../weather-service
cp .env.example .env
```

Nội dung `.env`:
```bash
APP_NAME=weather-service
ENVIRONMENT=local
LOG_LEVEL=INFO

# OpenWeatherMap API
OPENWEATHER_API_KEY=your-api-key-here

# Database & Cache
DATABASE_URL=postgresql+psycopg2://trip:trip@postgres:5432/trip_hub
REDIS_URL=redis://redis:6379/0
```

🔑 **Lấy OpenWeather API Key**:
1. Đăng ký tại: https://openweathermap.org/api
2. Free tier: 1000 calls/day
3. Copy API key vào file `.env`

#### **2.4 Destination Service**

```bash
cd ../destination-service
cp .env.example .env
```

Nội dung `.env`:
```bash
APP_NAME=destination-service
ENVIRONMENT=local
LOG_LEVEL=INFO

# MySQL Database
DATABASE_URL=mysql://root:root@mysql:3306/destinations
```

#### **2.5 Itinerary Service**

```bash
cd ../itinerary-service-json
cp .env.example .env
```

Nội dung `.env`:
```bash
APP_NAME=itinerary-service
ENVIRONMENT=local
LOG_LEVEL=INFO

# PostgreSQL (shared với middleware)
DATABASE_URL=postgresql+psycopg2://trip:trip@postgres:5432/trip_hub
```

---

## 🐳 Triển Khai với Docker

### **Step 1: Build Docker Images**

Từ thư mục gốc `trip-hub`:

```bash
# Build tất cả services
docker compose build

# Expected output:
# [+] Building ...
# => [middleware-service] ...
# => [destination-service] ...
# => [weather-service] ...
# => [booking-service] ...
# => [itinerary-service] ...
```

Build có thể mất 5-10 phút lần đầu tiên.

### **Step 2: Start Services**

```bash
# Start tất cả containers trong background
docker compose up -d

# Expected output:
# [+] Running 8/8
# ✔ Container trip-hub-redis-1                Started
# ✔ Container trip-hub-postgres-1             Started
# ✔ Container trip-hub-mysql-1                Started
# ✔ Container trip-hub-destination-service-1  Started
# ✔ Container trip-hub-weather-service-1      Started
# ✔ Container trip-hub-booking-service-1      Started
# ✔ Container trip-hub-itinerary-service-1    Started
# ✔ Container trip-hub-middleware-service-1   Started
```

### **Step 3: Verify Services Status**

```bash
# Check container status
docker compose ps

# Expected output (all should be "Up" or "Up (healthy)"):
# NAME                               STATUS        PORTS
# trip-hub-middleware-service-1      Up (healthy)  0.0.0.0:9000->8000/tcp
# trip-hub-booking-service-1         Up            
# trip-hub-destination-service-1     Up            
# trip-hub-weather-service-1         Up            
# trip-hub-itinerary-service-1       Up            
# trip-hub-postgres-1                Up            0.0.0.0:5432->5432/tcp
# trip-hub-mysql-1                   Up            0.0.0.0:3306->3306/tcp
# trip-hub-redis-1                   Up            0.0.0.0:6379->6379/tcp
```

### **Step 4: Check Health Endpoints**

```bash
# Kiểm tra API Gateway
curl http://localhost:9000/health

# Expected response:
# {
#   "status": "ok",
#   "service": "middleware-service",
#   "forwarding_to": ["booking", "destination", "itinerary", "weather"]
# }
```

Nếu health check trả về OK, hệ thống đã sẵn sàng! 🎉

### **Step 5: View Logs (Optional)**

```bash
# Xem logs của tất cả services
docker compose logs -f

# Xem logs của một service cụ thể
docker compose logs -f middleware-service

# Stop log stream: Ctrl+C
```

---

## 🌐 Chạy Web Demo

### **Step 1: Start Web Server**

Trip Hub có web UI đơn giản để demo các tính năng.

```bash
# Từ thư mục gốc trip-hub
cd web

# Start web server với Python
python -m http.server 8080

# Hoặc với Python 3
python3 -m http.server 8080

# Expected output:
# Serving HTTP on :: port 8080 (http://[::]:8080/) ...
```

### **Step 2: Open Web UI**

1. Mở browser và truy cập: **http://localhost:8080**
2. Trang web sẽ hiển thị Trip Hub UI

### **Step 3: Configure API Base URL**

Trên web UI, set API base URL:
```
http://localhost:9000
```

Hoặc nếu có setting page, điền:
- **API Gateway URL**: `http://localhost:9000`

---

## 📖 Hướng Dẫn Sử Dụng

### **Demo Flow 1: User Authentication**

#### **1.1 Register New User**

**Via Web UI**:
1. Click "Register" button
2. Nhập username: `demo_user`
3. Nhập password: `demo123`
4. Click "Submit"

**Via cURL**:
```bash
curl -X POST http://localhost:9000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "demo123"
  }'

# Response:
# {"message": "registered"}
```

#### **1.2 Login**

**Via Web UI**:
1. Click "Login"
2. Nhập username: `demo_user`
3. Nhập password: `demo123`
4. Click "Submit"
5. Token sẽ được lưu tự động

**Via cURL**:
```bash
TOKEN=$(curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "demo123"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"
```

Lưu token này để dùng cho các requests tiếp theo.

### **Demo Flow 2: Discover Destinations**

#### **2.1 Browse Destinations**

**Via Web UI**:
1. Navigate to "Destinations" tab
2. Click "Search" hoặc browse list
3. Có thể filter theo country, category

**Via cURL**:
```bash
# List all destinations
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/destination/destinations?page=1&per_page=10"

# Search destinations
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/destination/destinations?query=paris"

# Filter by country
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/destination/destinations?country=Thailand"
```

#### **2.2 Get Destination Details**

**Via cURL**:
```bash
# Get details of destination ID 1
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:9000/api/v1/destination/destinations/1
```

### **Demo Flow 3: Check Weather**

#### **3.1 Current Weather**

**Via Web UI**:
1. Navigate to "Weather" tab
2. Nhập city name: `Bangkok`
3. Click "Get Weather"

**Via cURL**:
```bash
# Current weather for Bangkok
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/weather/current/Bangkok"

# Response example:
# {
#   "city": "Bangkok",
#   "temperature": 32.5,
#   "weather": "Clear sky",
#   "humidity": 65,
#   "wind_speed": 3.5
# }
```

#### **3.2 5-Day Forecast**

**Via cURL**:
```bash
# 5-day forecast for Paris
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/weather/forecast/Paris"
```

### **Demo Flow 4: Search Flights & Hotels**

#### **4.1 Search Cities**

**Via cURL**:
```bash
# Get all cities
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/booking/cities?limit=50"

# Search by keyword
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/booking/cities?keyword=bangkok"

# Filter by country
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/booking/cities?country_code=VN"
```

#### **4.2 Search Flights**

**Via Web UI**:
1. Navigate to "Flights" tab
2. Select origin: `HAN` (Hanoi)
3. Select destination: `BKK` (Bangkok)
4. Choose dates
5. Select passengers
6. Click "Search"

**Via cURL**:
```bash
curl -X POST http://localhost:9000/api/v1/booking/flights/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "HAN",
    "destination": "BKK",
    "departure_date": "2025-06-01",
    "return_date": "2025-06-07",
    "adults": 2,
    "currency": "USD",
    "travel_class": "ECONOMY",
    "max_results": 5
  }'
```

#### **4.3 Search Hotels**

**Via cURL**:
```bash
curl -X POST http://localhost:9000/api/v1/booking/hotels/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "city_code": "BKK",
    "check_in_date": "2025-06-01",
    "check_out_date": "2025-06-07",
    "adults": 2,
    "rooms": 1,
    "currency": "USD",
    "max_results": 5
  }'
```

### **Demo Flow 5: Plan Itinerary**

#### **5.1 Create Trip Itinerary**

**Via Web UI**:
1. Navigate to "My Trips" tab
2. Click "Create New Trip"
3. Enter:
   - Title: `Summer Vacation in Thailand`
   - Start date: `2025-06-01`
   - End date: `2025-06-07`
   - Description: `One week trip to Bangkok and Phuket`
4. Click "Create"

**Via cURL**:
```bash
# Create itinerary
ITINERARY_ID=$(curl -X POST http://localhost:9000/api/v1/itinerary/itineraries \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Summer Vacation in Thailand",
    "start_date": "2025-06-01",
    "end_date": "2025-06-07",
    "description": "One week trip to Bangkok and Phuket"
  }' | jq -r '.id')

echo "Itinerary ID: $ITINERARY_ID"
```

#### **5.2 Add Activities**

**Via cURL**:
```bash
# Add activity 1: Visit Grand Palace
curl -X POST http://localhost:9000/api/v1/itinerary/activities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"itinerary_id\": \"$ITINERARY_ID\",
    \"title\": \"Visit Grand Palace\",
    \"start_time\": \"2025-06-02T09:00:00\",
    \"end_time\": \"2025-06-02T12:00:00\",
    \"location\": \"Grand Palace, Bangkok\",
    \"note\": \"Book tickets in advance\"
  }"

# Add activity 2: Beach day
curl -X POST http://localhost:9000/api/v1/itinerary/activities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"itinerary_id\": \"$ITINERARY_ID\",
    \"title\": \"Patong Beach\",
    \"start_time\": \"2025-06-04T10:00:00\",
    \"end_time\": \"2025-06-04T18:00:00\",
    \"location\": \"Patong Beach, Phuket\",
    \"note\": \"Bring sunscreen\"
  }"
```

#### **5.3 List Itineraries & Activities**

**Via cURL**:
```bash
# List all my itineraries
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:9000/api/v1/itinerary/itineraries

# List activities for specific itinerary
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/itinerary/activities/$ITINERARY_ID"
```

### **Demo Flow 6: Complete User Journey**

**End-to-End Example**:

```bash
# 1. Register & Login
curl -X POST http://localhost:9000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"traveler1","password":"pass123"}'

TOKEN=$(curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"traveler1","password":"pass123"}' \
  | jq -r '.access_token')

# 2. Discover Paris
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/destination/destinations?query=paris"

# 3. Check Paris weather
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9000/api/v1/weather/forecast/Paris"

# 4. Search flights HAN → CDG (Paris)
curl -X POST http://localhost:9000/api/v1/booking/flights/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "origin":"HAN","destination":"CDG",
    "departure_date":"2025-07-01","return_date":"2025-07-14",
    "adults":2,"currency":"USD"
  }'

# 5. Create trip
TRIP_ID=$(curl -X POST http://localhost:9000/api/v1/itinerary/itineraries \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Paris Summer Trip",
    "start_date":"2025-07-01","end_date":"2025-07-14",
    "description":"Two weeks in Paris"
  }' | jq -r '.id')

# 6. Add Eiffel Tower visit
curl -X POST http://localhost:9000/api/v1/itinerary/activities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"itinerary_id\":\"$TRIP_ID\",
    \"title\":\"Eiffel Tower\",
    \"start_time\":\"2025-07-02T10:00:00\",
    \"end_time\":\"2025-07-02T12:00:00\",
    \"location\":\"Paris\",
    \"note\":\"Book tickets online\"
  }"

# 7. View my trips
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:9000/api/v1/itinerary/itineraries
```

---

## 🔍 Troubleshooting

### **Problem 1: Docker containers không start**

**Symptoms**:
```bash
docker compose ps
# Shows "Exited" or "Restarting"
```

**Solutions**:
```bash
# Check logs
docker compose logs middleware-service

# Rebuild và restart
docker compose down
docker compose build --no-cache
docker compose up -d

# Check Docker resources
docker system df
# Ensure enough disk space
```

### **Problem 2: Health check failed**

**Symptoms**:
```bash
curl http://localhost:9000/health
# Connection refused or timeout
```

**Solutions**:
```bash
# Wait 30-60 seconds for services to start
sleep 30
curl http://localhost:9000/health

# Check if port is listening
lsof -i :9000
# Or on Windows
netstat -an | findstr 9000

# Check container logs
docker compose logs middleware-service
```

### **Problem 3: JWT token invalid (401)**

**Symptoms**:
```json
{"detail": "Invalid token"}
```

**Solutions**:
- Token expires after 1 hour - login lại
- Verify token format: `Authorization: Bearer <token>`
- Check không có spaces hoặc newlines trong token

```bash
# Debug: verify token
echo $TOKEN
# Should be long string: eyJhbGci...

# Get new token
TOKEN=$(curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","password":"demo123"}' \
  | jq -r '.access_token')
```

### **Problem 4: External API errors**

**Amadeus API errors**:
```json
{"detail": "Authentication failed"}
```

**Solutions**:
- Verify `AMADEUS_API_KEY` và `AMADEUS_API_SECRET` trong `.env`
- Check API quota: https://developers.amadeus.com
- Try với different search parameters

**OpenWeatherMap errors**:
```json
{"error": "Invalid API key"}
```

**Solutions**:
- Verify `OPENWEATHER_API_KEY` trong `.env`
- Check quota: https://openweathermap.org/api
- Ensure API key is activated (có thể mất 10 phút)

### **Problem 5: Database connection errors**

**Symptoms**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions**:
```bash
# Check PostgreSQL
docker exec trip-hub-postgres-1 pg_isready -U trip

# Check MySQL
docker exec trip-hub-mysql-1 mysqladmin ping -u root -proot

# Check Redis
docker exec trip-hub-redis-1 redis-cli ping

# Restart databases
docker compose restart postgres mysql redis

# Wait and try again
sleep 10
```

### **Problem 6: Port conflicts**

**Symptoms**:
```
Error: bind: address already in use
```

**Solutions**:
```bash
# Check what's using port 9000
lsof -i :9000
# Kill the process or change Docker port

# Change port in docker-compose.yml
# middleware-service:
#   ports:
#     - "9001:8000"  # Use 9001 instead
```

### **Problem 7: Web UI không load**

**Symptoms**:
- Page không hiển thị
- CORS errors in browser console

**Solutions**:
1. Verify web server đang chạy:
   ```bash
   # Check if port 8080 is listening
   lsof -i :8080
   ```

2. Check CORS trong middleware service
   - Middleware đã enable CORS cho all origins
   
3. Hard refresh browser: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

4. Check browser console for errors (F12)

### **Problem 8: Performance slow**

**Solutions**:
```bash
# Check resource usage
docker stats

# If containers using too much memory/CPU:
# - Reduce number of services running
# - Increase Docker memory limit
# - Close other applications

# Restart Docker
# On Mac/Windows: Restart Docker Desktop
# On Linux:
sudo systemctl restart docker
```

---

## 🧹 Cleanup & Maintenance

### **Stop Services**

```bash
# Stop services (giữ data)
docker compose stop

# Start lại
docker compose start
```

### **Remove Containers**

```bash
# Xóa containers nhưng giữ volumes (data)
docker compose down

# Xóa containers VÀ volumes (reset toàn bộ)
docker compose down -v
```

### **View Logs**

```bash
# Logs của tất cả services
docker compose logs

# Logs của service cụ thể
docker compose logs middleware-service

# Follow logs (live)
docker compose logs -f

# Last 100 lines
docker compose logs --tail=100
```

### **Database Backup**

```bash
# Backup PostgreSQL
docker exec trip-hub-postgres-1 pg_dump -U trip trip_hub > backup.sql

# Restore
cat backup.sql | docker exec -i trip-hub-postgres-1 psql -U trip trip_hub

# Backup MySQL
docker exec trip-hub-mysql-1 mysqldump -u root -proot destinations > destinations_backup.sql

# Restore
cat destinations_backup.sql | docker exec -i trip-hub-mysql-1 mysql -u root -proot destinations
```

---

## 📚 Additional Resources

### **API Documentation**
- **Swagger UI**: http://localhost:9000/api/docs
- **ReDoc**: http://localhost:9000/api/redoc

### **Service-Specific Docs**
- [Middleware Service](../services/middleware-service/README.md)
- [Destination Service](../services/destination-service/README.md)
- [Weather Service](../services/weather-service/README.md)
- [Booking Service](../services/booking-service/README.md)
- [Itinerary Service](../services/itinerary-service-json/README.md)

### **Architecture**
- [System README](../README.md)
- [Deployment Guide](../DEPLOYMENT_GUIDE.md)

---

## ✅ Quick Reference

### **Essential Commands**

```bash
# Start everything
docker compose up -d --build

# Check status
docker compose ps
curl http://localhost:9000/health

# View logs
docker compose logs -f middleware-service

# Stop everything
docker compose down

# Complete cleanup
docker compose down -v
```

### **Common API Calls**

```bash
# Register
curl -X POST http://localhost:9000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"pass123"}'

# Login
TOKEN=$(curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"pass123"}' \
  | jq -r '.access_token')

# List destinations
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:9000/api/v1/destination/destinations

# Weather
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:9000/api/v1/weather/current/Bangkok

# Create trip
curl -X POST http://localhost:9000/api/v1/itinerary/itineraries \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Trip","start_date":"2025-07-01","end_date":"2025-07-07","description":"Vacation"}'
```

---

## 🎯 Demo Checklist

Để demo hoàn chỉnh, thực hiện theo checklist:

- [ ] **1. Setup**
  - [ ] Docker installed và running
  - [ ] Repository cloned
  - [ ] Environment variables configured
  - [ ] All services built: `docker compose build`

- [ ] **2. Start System**
  - [ ] Services started: `docker compose up -d`
  - [ ] Health check passed: `curl http://localhost:9000/health`
  - [ ] Web UI accessible: http://localhost:8080

- [ ] **3. Demo Authentication**
  - [ ] Register new user
  - [ ] Login và get JWT token
  - [ ] Verify token works

- [ ] **4. Demo Destination Search**
  - [ ] List destinations
  - [ ] Search by keyword
  - [ ] Filter by country
  - [ ] View destination details

- [ ] **5. Demo Weather**
  - [ ] Get current weather
  - [ ] Get 5-day forecast

- [ ] **6. Demo Booking**
  - [ ] Search cities
  - [ ] Search flights
  - [ ] Search hotels

- [ ] **7. Demo Itinerary**
  - [ ] Create itinerary
  - [ ] Add activities
  - [ ] List trips
  - [ ] View trip details

- [ ] **8. Cleanup**
  - [ ] Stop services: `docker compose down`

---

**Happy Deploying! 🚀**

Nếu có vấn đề, check [Troubleshooting](#troubleshooting) section hoặc xem logs: `docker compose logs -f`
