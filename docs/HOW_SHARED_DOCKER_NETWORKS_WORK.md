# Cơ Chế Hoạt Động của Shared Docker Network

## 1. Kiến Trúc Docker Network

```
┌─────────────────────────────────────────────────────────────┐
│                     HOST MACHINE                             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           DOCKER BRIDGE NETWORK (trip-network)       │  │
│  │                                                       │  │
│  │  ┌──────────────────┐  ┌──────────────────┐         │  │
│  │  │  middleware      │  │  destination     │         │  │
│  │  │  Container       │  │  Container       │         │  │
│  │  │                  │  │                  │         │  │
│  │  │ IP: 172.18.0.2   │  │ IP: 172.18.0.3   │         │  │
│  │  │ Port: 8000       │  │ Port: 8000       │         │  │
│  │  └──────────────────┘  └──────────────────┘         │  │
│  │           ↑                      ↑                   │  │
│  │           └──────────────────────┘                   │  │
│  │                                                       │  │
│  │  ┌──────────────────┐  ┌──────────────────┐         │  │
│  │  │  weather         │  │  booking         │         │  │
│  │  │  Container       │  │  Container       │         │  │
│  │  │                  │  │                  │         │  │
│  │  │ IP: 172.18.0.4   │  │ IP: 172.18.0.5   │         │  │
│  │  │ Port: 8000       │  │ Port: 8000       │         │  │
│  │  └──────────────────┘  └──────────────────┘         │  │
│  │                                                       │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │     EMBEDDED DNS SERVER (127.0.0.11:53)      │   │  │
│  │  │  - middleware-service → 172.18.0.2           │   │  │
│  │  │  - destination-service → 172.18.0.3          │   │  │
│  │  │  - weather-service → 172.18.0.4              │   │  │
│  │  │  - booking-service → 172.18.0.5              │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  │                                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              HOST NETWORK INTERFACE                  │  │
│  │  - localhost:9000 → middleware-service:8000          │  │
│  │  - localhost:8001 → destination-service:8000 (opt)   │  │
│  │  - localhost:8004 → weather-service:8000 (opt)       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 2. Quy Trình DNS Resolution Chi Tiết

### **Step 1: Container Gửi Request**
```python
# Middleware container gọi destination-service
response = await client.request(
    url="http://destination-service:8000/api/v1/destinations"
)
```

### **Step 2: OS Resolver Lookup**
```
Middleware Container (172.18.0.2)
    ↓
Cần resolve: "destination-service"
    ↓
Kiểm tra /etc/resolv.conf trong container:
    nameserver 127.0.0.11  ← Docker Embedded DNS
    nameserver 8.8.8.8     ← Fallback (Google DNS)
```

### **Step 3: Docker Embedded DNS Server**
```
Docker DNS Server (127.0.0.11:53)
    ↓
Kiểm tra DNS cache:
    - destination-service → 172.18.0.3 ✓ (Tìm thấy)
    ↓
Trả về: 172.18.0.3
```

### **Step 4: Container Gửi Packet**
```
Middleware Container (172.18.0.2)
    ↓
Tạo TCP connection tới 172.18.0.3:8000
    ↓
Gửi HTTP request
```

### **Step 5: Network Bridge Chuyển Tiếp**
```
Docker Bridge (trip-network)
    ↓
Nhận packet từ 172.18.0.2
    ↓
Chuyển tiếp tới 172.18.0.3
    ↓
Destination Container nhận packet
```

## 3. So Sánh: Với vs Không Có Network

### **❌ KHÔNG CÓ DOCKER NETWORK**
```
Middleware Container
    ↓
Cần gọi: http://localhost:8001/api/v1/destinations
    ↓
localhost = 127.0.0.1 (loopback interface)
    ↓
Tìm port 8001 trên HOST MACHINE
    ↓
HOST chuyển tiếp tới Destination Container:8000
    ↓
Destination Container trả response
    ↓
HOST chuyển tiếp lại tới Middleware Container

❌ Vấn đề:
- Phải đi qua HOST (overhead)
- Phụ thuộc vào port mapping
- Không an toàn (ai cũng truy cập được)
- Khó scale (port conflicts)
```

### **✅ CÓ DOCKER NETWORK**
```
Middleware Container
    ↓
Cần gọi: http://destination-service:8000/api/v1/destinations
    ↓
Docker DNS resolve: destination-service → 172.18.0.3
    ↓
Tạo direct connection tới 172.18.0.3:8000
    ↓
Destination Container nhận request trực tiếp
    ↓
Trả response trực tiếp

✅ Lợi ích:
- Direct communication (nhanh hơn)
- Service discovery tự động
- Không cần hardcode IPs
- An toàn (isolated network)
- Dễ scale (thêm containers)
```

## 4. Docker DNS Cache & Service Discovery

### **Khi Container Khởi Động**
```
1. Docker Daemon nhận lệnh: docker-compose up
2. Tạo network "trip-network"
3. Khởi động middleware-service container
   - Gán IP: 172.18.0.2
   - Đăng ký DNS: middleware-service → 172.18.0.2
4. Khởi động destination-service container
   - Gán IP: 172.18.0.3
   - Đăng ký DNS: destination-service → 172.18.0.3
5. Khởi động weather-service container
   - Gán IP: 172.18.0.4
   - Đăng ký DNS: weather-service → 172.18.0.4
```

### **DNS Lookup Process**
```
Container gọi: destination-service:8000
    ↓
Gethostbyname("destination-service")
    ↓
Query Docker DNS: 127.0.0.11:53
    ↓
Docker DNS trả về: 172.18.0.3
    ↓
Container cache kết quả
    ↓
Lần sau gọi nhanh hơn (từ cache)
```

## 5. Network Isolation

```
┌─────────────────────────────────────────┐
│   DOCKER BRIDGE NETWORK (trip-network)  │
│                                         │
│  ✓ middleware-service ↔ destination    │
│  ✓ middleware-service ↔ weather        │
│  ✓ middleware-service ↔ booking        │
│  ✓ destination ↔ weather (nếu cần)     │
│                                         │
└─────────────────────────────────────────┘
         ↓ (Port Mapping)
┌─────────────────────────────────────────┐
│        HOST NETWORK (localhost)         │
│                                         │
│  ✓ localhost:9000 → middleware:8000    │
│  ✗ localhost:8001 → destination (KHÔNG)|
│  ✗ localhost:8004 → weather (KHÔNG)    │
│  ✗ localhost:8003 → booking (KHÔNG)    │
│                                         │
└─────────────────────────────────────────┘
```

## 6. Ví Dụ docker-compose.yml Chuẩn

```yaml
version: '3.8'

networks:
  trip-network:
    driver: bridge

services:
  middleware-service:
    build: ./services/middleware-service
    ports:
      - "9000:8000"  # Chỉ expose middleware
    networks:
      - trip-network
    environment:
      DESTINATION_SERVICE_URL: http://destination-service:8000
      WEATHER_SERVICE_URL: http://weather-service:8000
      BOOKING_SERVICE_URL: http://booking-service:8000

  destination-service:
    build: ./services/destination-service
    networks:
      - trip-network
    # Không expose port (chỉ internal)

  weather-service:
    build: ./services/weather-service
    networks:
      - trip-network
    # Không expose port (chỉ internal)

  booking-service:
    build: ./services/booking-service
    networks:
      - trip-network
    # Không expose port (chỉ internal)
```

## 7. Kiểm Tra Network Hoạt Động

```bash
# Xem các networks
docker network ls

# Xem chi tiết network
docker network inspect trip-network

# Output:
# {
#   "Name": "trip-network",
#   "Containers": {
#     "abc123...": {
#       "Name": "middleware-service",
#       "IPv4Address": "172.18.0.2/16"
#     },
#     "def456...": {
#       "Name": "destination-service",
#       "IPv4Address": "172.18.0.3/16"
#     }
#   }
# }

# Test DNS từ container
docker exec middleware-service nslookup destination-service
# Output: Address: 172.18.0.3
```

## Tóm Tắt

**Docker Network hoạt động qua:**
1. **Embedded DNS Server** - Tự động resolve tên service
2. **Bridge Driver** - Kết nối containers trong network
3. **IP Allocation** - Gán IP tự động cho mỗi container
4. **Service Discovery** - DNS cache tên service
5. **Network Isolation** - Chỉ containers trong network mới giao tiếp được

Đây là cơ chế cho phép microservices giao tiếp **an toàn, nhanh, và tự động** mà không cần hardcode IPs hay ports.