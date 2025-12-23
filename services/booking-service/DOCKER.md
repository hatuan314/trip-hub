# Docker Deployment Guide - Booking Service

## Yêu cầu

- Docker Engine 20.10+
- Docker Compose 2.0+

## Cấu trúc Docker

### Dockerfile
- Base image: `python:3.11-slim`
- Port: 8000
- Dependencies: Được cài đặt từ `requirements.txt`
- Working directory: `/app`

### Docker Compose
Service bao gồm:
- **booking-service**: FastAPI application
- **redis**: Redis cache server

## Cách sử dụng

### 1. Cấu hình môi trường

Tạo file `.env` từ `.env.example`:
```bash
cp .env.example .env
```

Cập nhật các giá trị trong `.env`:
```env
AMADEUS_API_KEY=your_api_key
AMADEUS_API_SECRET=your_api_secret
```

### 2. Build và chạy với Docker Compose

```bash
# Build và start tất cả services
docker-compose up -d --build

# Xem logs
docker-compose logs -f booking-service

# Stop services
docker-compose down

# Stop và xóa volumes
docker-compose down -v
```

### 3. Build và chạy chỉ với Docker

```bash
# Build image
docker build -t booking-service:latest .

# Run container (cần Redis riêng)
docker run -d \
  --name booking-service \
  -p 8000:8000 \
  --env-file .env \
  booking-service:latest
```

## Kiểm tra service

### Health check
```bash
curl http://localhost:8000/health
```

### API Documentation
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Quản lý

### Xem logs
```bash
# Tất cả services
docker-compose logs -f

# Chỉ booking-service
docker-compose logs -f booking-service

# Chỉ redis
docker-compose logs -f redis
```

### Restart service
```bash
docker-compose restart booking-service
```

### Rebuild sau khi thay đổi code
```bash
docker-compose up -d --build booking-service
```

### Truy cập container
```bash
docker-compose exec booking-service bash
```

### Xem trạng thái
```bash
docker-compose ps
```

## Volumes

- **redis-data**: Lưu trữ dữ liệu Redis persistent
- **./src**: Mount source code để development (hot reload)
- **./logs**: Mount thư mục logs

## Network

- **booking-network**: Bridge network cho communication giữa services

## Troubleshooting

### Service không start được
```bash
# Xem logs chi tiết
docker-compose logs booking-service

# Kiểm tra container status
docker-compose ps
```

### Redis connection failed
```bash
# Kiểm tra Redis đang chạy
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### Port đã được sử dụng
Thay đổi port mapping trong `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Thay 8001 bằng port khác
```

## Production Deployment

Để deploy production, tạo file `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  booking-service:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DEBUG=False
    restart: always
```

Chạy với:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
