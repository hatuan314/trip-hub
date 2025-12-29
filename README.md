# Trip Hub - Microservices Travel Planning Platform

**Trip Hub** là hệ thống microservices hoàn chỉnh cho việc lập kế hoạch và quản lý chuyến du lịch. Hệ thống được xây dựng với kiến trúc phân tán, bao gồm **5 microservices** độc lập tương tác qua **API Gateway**, cung cấp các tính năng từ tìm kiếm điểm đến, dự báo thời tiết, đặt vé máy bay/khách sạn, đến quản lý lịch trình du lịch.

---

## 📋 Mục Lục

1. [Tổng Quan Hệ Thống](#tổng-quan-hệ-thống)
2. [Phân Tích Yêu Cầu](#phân-tích-yêu-cầu)
3. [Kiến Trúc Microservices](#kiến-trúc-microservices)
4. [API Gateway & Routing](#api-gateway--routing)
5. [Giải Thích Hoạt Động](#giải-thích-hoạt-động)
6. [Deployment Guide](#deployment-guide)
7. [Service Documentation](#service-documentation)

---

## 🌟 Tổng Quan Hệ Thống

### **Tính Năng Chính**

Trip Hub cung cấp một nền tảng toàn diện cho travel planning:

1. 🔐 **User Authentication & Authorization** - JWT-based security
2. 🌍 **Destination Discovery** - Khám phá điểm đến du lịch
3. ☀️ **Weather Forecasting** - Dự báo thời tiết cho chuyến đi
4. ✈️ **Flight & Hotel Booking** - Tìm kiếm vé máy bay và khách sạn
5. 📅 **Itinerary Management** - Quản lý lịch trình và hoạt động

### **Tech Stack**

- **Backend**: Python 3.11+, FastAPI
- **API Gateway**: Custom FastAPI proxy với JWT authentication
- **Databases**: 
  - PostgreSQL (user data, itineraries)
  - MySQL (destinations)
- **External APIs**: 
  - OpenWeatherMap API (weather)
  - Amadeus API (flights & hotels)
- **Containerization**: Docker & Docker Compose
- **Communication**: HTTP/REST, synchronous
- **Authentication**: JWT (JSON Web Tokens)

### **Architecture Highlights**

✅ **Microservices Architecture** - 5 độc lập services  
✅ **API Gateway Pattern** - Single entry point với centralized auth  
✅ **Service Discovery** - Static configuration-based routing  
✅ **Database per Service** - Polyglot persistence  
✅ **External API Integration** - Real-time data từ third-party  
✅ **Containerized Deployment** - Docker Compose orchestration  

---

## 📌 Phân Tích Yêu Cầu

Hệ thống được thiết kế để đáp ứng các yêu cầu sau:

### **1. Functional Requirements**

#### **User Management**
- User registration và login
- JWT token-based authentication
- Shared user database giữa Middleware và Itinerary services
- Token expiration (1 hour)

#### **Destination Discovery**
- Browse danh sách điểm đến du lịch
- Search destinations theo keyword
- Filter theo country, category, rating
- Pagination support
- Destination details với description, attractions

#### **Weather Information**
- Current weather cho một location
- 5-day weather forecast
- Temperature, humidity, wind speed, conditions
- Weather icons và descriptions
- Support multiple cities worldwide

#### **Flight & Hotel Search**
- Tìm kiếm chuyến bay giữa 2 sân bay
- Filter theo travel class, non-stop, price
- Tìm kiếm khách sạn theo thành phố
- Room availability và pricing
- City/airport reference data
- Real-time data từ Amadeus API

#### **Itinerary Planning**
- Tạo travel itineraries (trips)
- Add activities vào itineraries
- Date range management
- Activity scheduling với time slots
- User-specific data isolation

### **2. Non-Functional Requirements**

#### **Security**
- JWT authentication cho protected endpoints
- User data isolation
- CORS support cho web client
- ⚠️ **Current Limitation**: Plain text passwords (development only)

#### **Performance**
- External API caching (planned)
- Connection pooling cho databases
- Async/await cho I/O operations
- HTTP timeout handling (30s)

#### **Scalability**
- Stateless services (horizontal scaling ready)
- Database per service (independent scaling)
- Containerized deployment

#### **Reliability**
- Error handling và logging
- Health check endpoints
- Automatic database table creation
- Transaction support

#### **Maintainability**
- Clean Architecture patterns
- Repository pattern cho data access
- Dependency injection
- Comprehensive documentation

---

## 🏗️ Kiến Trúc Microservices

### **System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Client                            │
│                    (React/Vue/Angular)                       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         │ Port: 9000
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   Middleware Service                         │
│                     (API Gateway)                            │
│  • JWT Authentication                                        │
│  • Request Routing                                           │
│  • Service Discovery                                         │
│  • User Management                                           │
└──┬──────┬──────┬──────┬──────────────────────────────────┬──┘
   │      │      │      │                                  │
   │      │      │      │      Internal Network            │
   │      │      │      │                                  │
   ↓      ↓      ↓      ↓                                  ↓
┌──────┐┌──────┐┌──────┐┌──────────────────────┐┌────────────┐
│Dest  ││Weather││Book  ││   Itinerary Service  ││  External  │
│Service││Service││Service││                     ││    APIs    │
│      ││      ││      ││  • Itineraries        ││            │
│MySQL ││OpenWea││Amadeus││  • Activities        ││• Amadeus  │
│      ││therMap││API   ││  • PostgreSQL         ││• OpenWea  │
└──────┘└──────┘└──────┘└─────────────────────┘└────────────┘
  8001    8002    8000             8000              External
```

### **Services Overview**

| Service | Port | Database | External API | Responsibility |
|---------|------|----------|--------------|----------------|
| **Middleware** | 9000 | PostgreSQL | - | API Gateway, Auth, Routing |
| **Destination** | 8001 | MySQL | - | Destination catalog |
| **Weather** | 8002 | - | OpenWeatherMap | Weather forecasts |
| **Booking** | 8000 | - | Amadeus | Flight/Hotel search |
| **Itinerary** | 8000 | PostgreSQL (shared) | - | Trip planning |

### **Service Details**

#### **1. Middleware Service (API Gateway)**
- **Tech**: FastAPI, PostgreSQL, JWT
- **Port**: 9000
- **Responsibilities**:
  - Centralized authentication (JWT)
  - Request routing to downstream services
  - Service discovery via static config
  - User registration & login
  - Wrapper endpoints với OpenAPI docs
  - Error handling (401, 404, 502, 504)
- **[📖 Documentation](./services/middleware-service/README.md)**

#### **2. Destination Service**
- **Tech**: FastAPI, MySQL
- **Port**: 8001
- **Responsibilities**:
  - Destination catalog management
  - Search & filter destinations
  - Country, category, rating filters
  - Pagination support
  - Destination details
- **[📖 Documentation](./services/destination-service/README.md)**

#### **3. Weather Service**
- **Tech**: FastAPI, OpenWeatherMap API
- **Port**: 8002
- **Responsibilities**:
  - Current weather data
  - 5-day forecast
  - Weather conditions & icons
  - Temperature, humidity, wind
  - Support multiple cities
- **[📖 Documentation](./services/weather-service/README.md)**

#### **4. Booking Service**
- **Tech**: FastAPI, Amadeus API
- **Port**: 8000
- **Responsibilities**:
  - Flight search (origin → destination)
  - Hotel search (by city)
  - City/airport reference data
  - Real-time availability & pricing
  - OAuth2 token management
- **[📖 Documentation](./services/booking-service/README.md)**

#### **5. Itinerary Service**
- **Tech**: FastAPI, PostgreSQL, SQLAlchemy
- **Port**: 8000
- **Responsibilities**:
  - Travel itinerary CRUD
  - Activity management
  - User data isolation
  - Date/time scheduling
  - Shared user database
- **[📖 Documentation](./services/itinerary-service-json/README.md)**

---

## 🔌 API Gateway & Routing

### **API Gateway Pattern**

Middleware Service hoạt động như **API Gateway**, providing:

1. **Single Entry Point**: Tất cả client requests qua port 9000
2. **Authentication**: JWT validation trước khi routing
3. **Service Discovery**: Map service names → URLs
4. **Request Proxying**: Forward requests với preserved data
5. **Error Handling**: Unified error responses

### **Routing Rules**

```
Client Request → Middleware (9000) → Downstream Service

/api/v1/auth/*              → Middleware (local)
/api/v1/destination/*       → Destination Service (8001)
/api/v1/weather/*           → Weather Service (8002)
/api/v1/booking/*           → Booking Service (8000)
/api/v1/itinerary/*         → Itinerary Service (8000)
```

### **Authentication Flow**

```
1. User registers/login → Middleware
2. Middleware returns JWT token
3. Client includes token in subsequent requests
4. Middleware validates token
5. If valid → proxy to downstream service
6. If invalid → 401 Unauthorized
```

### **API Endpoints Summary**

#### **Public Endpoints (No Auth)**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /health` - Health checks
- `GET /api/v1/cities` - City reference data

#### **Protected Endpoints (JWT Required)**

**Destinations**:
- `GET /api/v1/destination/destinations` - List destinations
- `GET /api/v1/destination/destinations/{id}` - Get destination details
- `POST /api/v1/destination/destinations/search` - Search destinations

**Weather**:
- `GET /api/v1/weather/current/{city}` - Current weather
- `GET /api/v1/weather/forecast/{city}` - 5-day forecast

**Booking**:
- `POST /api/v1/booking/flights/search` - Search flights
- `POST /api/v1/booking/hotels/search` - Search hotels
- `GET /api/v1/booking/cities` - List cities

**Itinerary**:
- `POST /api/v1/itinerary/itineraries` - Create itinerary
- `GET /api/v1/itinerary/itineraries` - List user itineraries
- `POST /api/v1/itinerary/activities` - Create activity
- `GET /api/v1/itinerary/activities/{itinerary_id}` - List activities

---

## ⚙️ Giải Thích Hoạt Động

### **Flow 1: User Registration & Authentication**

```
Client
  ↓
POST /api/v1/auth/register
{username: "traveler1", password: "pass123"}
  ↓
Middleware Service (Port 9000)
  ├─→ Validate input (Pydantic)
  ├─→ Check user exists in PostgreSQL
  ├─→ Hash password (⚠️ plain text in current version)
  ├─→ Save user to database
  ├─→ Sync user to Itinerary Service database
  └─→ Return success

POST /api/v1/auth/login
{username: "traveler1", password: "pass123"}
  ↓
Middleware Service
  ├─→ Query user from PostgreSQL
  ├─→ Verify password
  ├─→ Create JWT token (1 hour expiry)
  │   • Secret: "SECRET" (hardcoded)
  │   • Algorithm: HS256
  │   • Payload: {sub: username, exp: timestamp}
  └─→ Return {access_token: "eyJhbGci..."}

Future Requests
  ↓
Authorization: Bearer eyJhbGci...
  ↓
Middleware validates JWT → Extract username → Proxy request
```

### **Flow 2: Search Destinations**

```
Client
  ↓
GET /api/v1/destination/destinations?country=Thailand&page=1
Authorization: Bearer <token>
  ↓
Middleware Service (9000)
  ├─→ Validate JWT token
  ├─→ Extract username from token
  ├─→ Build target URL: http://destination-service:8001/api/v1/destinations
  ├─→ Preserve query params: ?country=Thailand&page=1
  └─→ Forward request via httpx
      ↓
Destination Service (8001)
  ├─→ Query MySQL database
  │   SELECT * FROM destinations 
  │   WHERE country LIKE '%Thailand%'
  │   LIMIT 10 OFFSET 0
  ├─→ Apply filters (country, category, rating)
  ├─→ Calculate pagination (total pages, has_next)
  └─→ Return JSON response
      ↓
Middleware
  └─→ Forward response to Client
```

**Files involved**:
- `middleware-service/src/api/v1/endpoints/proxy.py` - Proxy logic
- `destination-service/src/infrastructure/destination_repo.py` - DB queries

### **Flow 3: Get Weather Forecast**

```
Client
  ↓
GET /api/v1/weather/forecast/Bangkok
Authorization: Bearer <token>
  ↓
Middleware Service
  ├─→ Validate JWT
  └─→ Proxy to Weather Service (8002)
      ↓
Weather Service
  ├─→ Call OpenWeatherMap API
  │   GET https://api.openweathermap.org/data/2.5/forecast
  │   ?q=Bangkok&appid=<api_key>&units=metric
  │
  ├─→ Transform response:
  │   • Extract 5-day forecast data
  │   • Group by date
  │   • Calculate avg temperature
  │   • Format weather conditions
  │
  └─→ Return structured forecast
      {
        "city": "Bangkok",
        "forecasts": [
          {
            "date": "2025-01-01",
            "temperature": {
              "min": 24, "max": 32, "avg": 28
            },
            "weather": "Clear sky",
            "icon": "01d"
          }
        ]
      }
```

**Files involved**:
- `weather-service/src/infrastructure/weather_api.py` - OpenWeatherMap client
- `weather-service/src/api/v1/endpoints/weather.py` - API endpoints

### **Flow 4: Search Flights (Amadeus Integration)**

```
Client
  ↓
POST /api/v1/booking/flights/search
Authorization: Bearer <token>
{
  "origin": "HAN",
  "destination": "BKK",
  "departure_date": "2025-06-01",
  "return_date": "2025-06-07",
  "adults": 2,
  "currency": "USD"
}
  ↓
Middleware → Booking Service (8000)
  ↓
Booking Service
  ├─→ Get Amadeus OAuth2 token
  │   POST https://test.api.amadeus.com/v1/security/oauth2/token
  │   • client_credentials grant
  │   • Cache token (30 min expiry)
  │
  ├─→ Search flights via Amadeus
  │   GET /v2/shopping/flight-offers
  │   ?originLocationCode=HAN
  │   &destinationLocationCode=BKK
  │   &departureDate=2025-06-01
  │   &returnDate=2025-06-07
  │   &adults=2
  │   &currencyCode=USD
  │
  └─→ Return flight offers (raw Amadeus response)
      {
        "meta": {"count": 10},
        "data": [
          {
            "id": "1",
            "price": {"total": "250.00", "currency": "USD"},
            "itineraries": [...]
          }
        ]
      }
```

**Files involved**:
- `booking-service/src/infrastructure/external/amadeus_client.py` - OAuth2 + API calls
- `booking-service/src/core/use_cases/search_flights.py` - Business logic

### **Flow 5: Create Trip Itinerary**

```
Client
  ↓
POST /api/v1/itinerary/itineraries
Authorization: Bearer <token>
{
  "title": "Summer Vacation",
  "start_date": "2025-07-01",
  "end_date": "2025-07-14",
  "description": "Two weeks in Europe"
}
  ↓
Middleware
  ├─→ Validate JWT
  ├─→ Extract username from token
  └─→ Proxy to Itinerary Service
      ↓
Itinerary Service (8000)
  ├─→ Validate JWT again (double auth)
  ├─→ Pydantic validation
  ├─→ Generate UUID for itinerary
  ├─→ Create Itinerary entity
  │   id = uuid.uuid4()
  │   username = "traveler1"
  │   title, start_date, end_date, description
  │
  ├─→ Save to PostgreSQL
  │   INSERT INTO itineraries (id, username, title, ...)
  │   VALUES ('550e...', 'traveler1', 'Summer Vacation', ...)
  │
  └─→ Return created itinerary
      {
        "id": "550e8400-...",
        "user": "traveler1",
        "title": "Summer Vacation",
        "start_date": "2025-07-01",
        "end_date": "2025-07-14",
        "description": "..."
      }

Add Activity to Itinerary
  ↓
POST /api/v1/itinerary/activities
{
  "itinerary_id": "550e8400-...",
  "title": "Eiffel Tower Visit",
  "start_time": "2025-07-02T10:00:00",
  "end_time": "2025-07-02T12:00:00",
  "location": "Paris",
  "note": "Book tickets"
}
  ↓
Itinerary Service
  ├─→ Validate ownership (username matches)
  ├─→ Generate UUID for activity
  ├─→ Save to activities table
  │   INSERT INTO activities (id, itinerary_id, username, ...)
  └─→ Return created activity
```

**Files involved**:
- `itinerary-service-json/src/infrastructure/itinerary_repo.py` - Itinerary CRUD
- `itinerary-service-json/src/infrastructure/activity_repo.py` - Activity CRUD

### **Flow 6: End-to-End Trip Planning**

```
Complete User Journey:

1. Register/Login
   POST /api/v1/auth/register → Middleware
   POST /api/v1/auth/login → Get JWT token

2. Discover Destinations
   GET /api/v1/destination/destinations?country=France
   → Browse Paris, Nice, Lyon

3. Check Weather
   GET /api/v1/weather/forecast/Paris
   → Plan dates based on weather

4. Search Flights
   POST /api/v1/booking/flights/search
   {origin: "HAN", destination: "CDG", dates...}
   → Find flight options

5. Search Hotels
   POST /api/v1/booking/hotels/search
   {city_code: "PAR", check_in, check_out...}
   → Find accommodation

6. Create Itinerary
   POST /api/v1/itinerary/itineraries
   {title: "Paris Trip", dates...}
   → Create trip plan

7. Add Activities
   POST /api/v1/itinerary/activities
   {itinerary_id, title: "Eiffel Tower", time...}
   → Schedule activities

All steps authenticated via JWT from step 1
```

---

## 🚀 Deployment Guide

### **Prerequisites**

- Docker & Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL, MySQL (or use Docker)

### **Quick Start with Docker**

```bash
# Clone repository
git clone <repo-url>
cd trip-hub

# Start all services
docker compose up -d --build

# Verify services
docker compose ps

# Check logs
docker compose logs -f middleware-service

# Stop all services
docker compose down
```

### **Service URLs**

| Service | URL | Health Check |
|---------|-----|--------------|
| Middleware (Gateway) | http://localhost:9000 | http://localhost:9000/health |
| Destination | http://localhost:8001 | http://localhost:8001/health |
| Weather | http://localhost:8002 | http://localhost:8002/health |
| Booking | http://localhost:8000 | http://localhost:8000/health |
| Itinerary | http://localhost:8003 | http://localhost:8003/health |

### **API Documentation**

- **Middleware API Docs**: http://localhost:9000/api/docs
- **Destination API Docs**: http://localhost:8001/api/docs
- **Weather API Docs**: http://localhost:8002/api/docs
- **Booking API Docs**: http://localhost:8000/api/docs
- **Itinerary API Docs**: http://localhost:8003/api/docs

### **Environment Configuration**

Mỗi service có `.env.example` file. Copy và customize:

```bash
# Example for Middleware Service
cd services/middleware-service
cp .env.example .env
# Edit .env với actual credentials
```

**Key Environment Variables**:
- `DATABASE_URL` - PostgreSQL/MySQL connection string
- `AMADEUS_API_KEY` - Amadeus API credentials
- `OPENWEATHER_API_KEY` - OpenWeatherMap API key
- `SECRET_KEY` - JWT secret (should be moved to env)

---

## 📚 Service Documentation

Chi tiết implementation của từng service:

### **1. Middleware Service (API Gateway)**
**[📖 Full Documentation](./services/middleware-service/README.md)**

- JWT Authentication & User Management
- Request Routing & Service Discovery
- Proxy Pattern Implementation
- Error Handling & CORS
- Wrapper Endpoints

### **2. Destination Service**
**[📖 Full Documentation](./services/destination-service/README.md)**

- MySQL Database Schema
- Search & Filter Implementation
- Pagination Logic
- Country/Category Management
- Repository Pattern

### **3. Weather Service**
**[📖 Full Documentation](./services/weather-service/README.md)**

- OpenWeatherMap API Integration
- Current Weather & Forecast
- Response Transformation
- Error Handling
- Temperature Unit Conversion

### **4. Booking Service**
**[📖 Full Documentation](./services/booking-service/README.md)**

- Amadeus API Integration (OAuth2)
- Flight Search Implementation
- Hotel Search (2-step process)
- City Reference Data
- Token Management & Caching

### **5. Itinerary Service**
**[📖 Full Documentation](./services/itinerary-service-json/README.md)**

- PostgreSQL with SQLAlchemy ORM
- Repository Pattern
- Itinerary & Activity Management
- User Data Isolation
- UUID Generation

---

## 🔍 Troubleshooting

### **Common Issues**

#### **Service not starting**
```bash
# Check logs
docker compose logs <service-name>

# Rebuild specific service
docker compose up -d --build <service-name>

# Check container status
docker compose ps
```

#### **Database connection errors**
- Verify DATABASE_URL in `.env`
- Ensure PostgreSQL/MySQL containers are running
- Check database credentials
- Wait for database initialization (30s)

#### **JWT token invalid**
- Token expires after 1 hour - login again
- Verify SECRET_KEY matches across services
- Check token format: `Authorization: Bearer <token>`

#### **External API errors**
- Verify API keys in `.env`
- Check API quota limits (Amadeus, OpenWeatherMap)
- Review API response in logs
- Validate request parameters

---

## 📝 Architecture Notes

### **Design Patterns Used**

- **API Gateway Pattern** - Middleware Service
- **Repository Pattern** - Data access layer
- **Dependency Injection** - FastAPI Depends
- **Proxy Pattern** - Request forwarding
- **OAuth2 Client Credentials** - Amadeus authentication

### **Security Considerations**

⚠️ **Current Limitations (Development Mode)**:
- Plain text passwords (NOT production ready!)
- Hardcoded JWT secrets
- No rate limiting
- No HTTPS
- Shared database credentials

✅ **Production Recommendations**:
- Implement bcrypt/argon2 password hashing
- Use environment variables for secrets
- Add rate limiting middleware
- Enable HTTPS/TLS
- Implement API key rotation
- Add request logging & monitoring

### **Database Strategy**

- **Database per Service** principle
- **Shared User Table** (Middleware ↔ Itinerary)
- **Polyglot Persistence**: PostgreSQL + MySQL
- No cross-service database calls
- Application-level data consistency

### **Communication Patterns**

- **Synchronous HTTP/REST** (all services)
- **No Event Bus** (current version)
- **No Message Queue**
- **Direct Service-to-Service** via API Gateway
- Future: Consider async messaging for better resilience

---

## 🎯 Future Improvements

### **1. Service Enhancements**

- **Caching Layer**: Redis for external API responses
- **Rate Limiting**: Protect against abuse
- **Circuit Breaker**: Resilience patterns
- **Service Mesh**: Istio/Linkerd for advanced routing

### **2. Security**

- Implement proper password hashing
- Move secrets to environment variables
- Add HTTPS/TLS support
- Implement OAuth2 scopes
- Add request signing

### **3. Observability**

- Centralized logging (ELK stack)
- Distributed tracing (Jaeger/Zipkin)
- Metrics collection (Prometheus)
- Monitoring dashboards (Grafana)
- Health checks & alerting

### **4. Testing**

- Unit tests for each service
- Integration tests
- E2E tests with test containers
- Load testing (Locust/k6)
- Contract testing between services

### **5. DevOps**

- CI/CD pipelines (GitHub Actions)
- Kubernetes deployment
- Auto-scaling policies
- Blue-green deployments
- Database migrations automation

---

## 📖 Additional Resources

- **[Deployment Guide](./DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[Microservice Improvements](./MICROSERVICE_IMPROVEMENTS.md)** - Enhancement roadmap
- **[Project Structure](./PROJECT_STRUCTURE.md)** - Detailed code organization

---

## 👥 Contributing

Contributions welcome! Please read the contribution guidelines and submit pull requests.

---

## 📄 License

[Your License Here]

---

**Project Status**: ✅ Development Complete  
**Production Ready**: ⚠️ Security improvements needed  
**Last Updated**: December 2024  
**Team**: Trip Hub Development Team