# 📁 Cấu Trúc Dự Án Trip Hub - Travel Planning Application

## 🎯 Tổng Quan

**Trip Hub** là hệ thống **microservices** hoàn chỉnh cho việc lập kế hoạch và quản lý chuyến du lịch, được xây dựng với **Python FastAPI**, tích hợp **PostgreSQL**, **MySQL**, **Redis**, và triển khai với **Docker Compose**.

### **Kiến Trúc Thực Tế**

- **5 Microservices**: Middleware (API Gateway), Destination, Weather, Booking, Itinerary
- **Pattern**: Clean Architecture, Repository Pattern, API Gateway Pattern
- **Communication**: HTTP/REST synchronous
- **Authentication**: JWT tokens (centralized tại Middleware)
- **Databases**: 
  - **PostgreSQL**: Users, Itineraries, Activities (shared giữa Middleware & Itinerary)
  - **MySQL**: Destinations catalog
  - **Redis**: Cache cho Booking & Weather services
- **External APIs**: 
  - **Amadeus API**: Flight & Hotel search
  - **OpenWeatherMap API**: Weather forecasting
- **Deployment**: Docker Compose với Docker network (trip-network)
- **Public Access**: Chỉ Middleware Service (port 9000)
- **Documentation**: Comprehensive README.md cho từng service

### **Tech Stack**

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic
- **HTTP Client**: httpx (async)
- **Containerization**: Docker + Docker Compose
- **Web UI**: Static HTML/CSS/JS

---

## 🧱 Cấu Trúc Thư Mục Thực Tế

```
trip-hub/
├── services/                                # 5 Microservices
│   │
│   ├── middleware-service/                  # ⭐ API Gateway + Authentication
│   │   ├── src/
│   │   │   ├── api/v1/                      # API Layer
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── auth.py              # POST /register, /login
│   │   │   │   │   ├── proxy.py             # Generic proxy /{service}/{path}
│   │   │   │   │   └── wrappers.py          # Wrapper endpoints (convenience)
│   │   │   │   ├── router.py                # Route aggregation
│   │   │   │   └── dependencies.py          # get_current_user (JWT auth)
│   │   │   │
│   │   │   ├── core/                        # Business Logic
│   │   │   │   ├── service_router.py        # ServiceRouter class (service discovery)
│   │   │   │   └── bootstrap.py             # Service URLs initialization
│   │   │   │
│   │   │   ├── infrastructure/              # Data Access Layer
│   │   │   │   ├── database/
│   │   │   │   │   ├── connection.py        # PostgreSQL connection
│   │   │   │   │   └── models.py            # User ORM model
│   │   │   │   └── user_repo.py             # User repository (create, get)
│   │   │   │
│   │   │   ├── schemas/
│   │   │   │   └── auth.py                  # UserRegister, UserLogin schemas
│   │   │   │
│   │   │   ├── config/
│   │   │   │   └── settings.py              # Service URLs, DATABASE_URL
│   │   │   │
│   │   │   ├── utils/
│   │   │   │   └── security.py              # JWT creation, password handling
│   │   │   │
│   │   │   └── main.py                      # FastAPI app, CORS, startup
│   │   │
│   │   ├── Dockerfile
│   │   ├── requirements.txt                 # fastapi, sqlalchemy, httpx, python-jose
│   │   ├── .env.example
│   │   └── README.md                        # ✅ Full documentation
│   │
│   ├── destination-service/                 # 📍 Destination Catalog (MySQL)
│   │   ├── src/
│   │   │   ├── api/v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   └── destinations.py      # GET /destinations, /destinations/{id}
│   │   │   │   └── router.py
│   │   │   │
│   │   │   ├── core/
│   │   │   │   └── use_cases/
│   │   │   │       └── get_destinations.py  # Business logic
│   │   │   │
│   │   │   ├── infrastructure/
│   │   │   │   ├── database/
│   │   │   │   │   ├── connection.py        # MySQL connection
│   │   │   │   │   └── models.py            # Destination model
│   │   │   │   └── destination_repo.py      # Repository (list, get, search, filter)
│   │   │   │
│   │   │   ├── schemas/
│   │   │   │   └── destination.py           # DestinationResponse, SearchRequest
│   │   │   │
│   │   │   ├── config/
│   │   │   │   └── settings.py              # DATABASE_URL (MySQL)
│   │   │   │
│   │   │   └── main.py
│   │   │
│   │   ├── Dockerfile
│   │   ├── requirements.txt                 # fastapi, mysql-connector-python
│   │   ├── .env.example
│   │   └── README.md                        # ✅ Full documentation
│   │
│   ├── weather-service/                     # ☀️ Weather Forecast (OpenWeatherMap)
│   │   ├── src/
│   │   │   ├── api/v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   └── weather.py           # GET /current/{city}, /forecast/{city}
│   │   │   │   └── router.py
│   │   │   │
│   │   │   ├── core/
│   │   │   │   └── use_cases/
│   │   │   │       ├── get_current_weather.py
│   │   │   │       └── get_forecast.py
│   │   │   │
│   │   │   ├── infrastructure/
│   │   │   │   ├── weather_api.py           # OpenWeatherMap API client
│   │   │   │   └── cache.py                 # Redis caching (optional)
│   │   │   │
│   │   │   ├── schemas/
│   │   │   │   └── weather.py               # WeatherResponse, ForecastResponse
│   │   │   │
│   │   │   ├── config/
│   │   │   │   └── settings.py              # OPENWEATHER_API_KEY, REDIS_URL
│   │   │   │
│   │   │   └── main.py
│   │   │
│   │   ├── Dockerfile
│   │   ├── requirements.txt                 # fastapi, httpx, redis
│   │   ├── .env.example
│   │   └── README.md                        # ✅ Full documentation
│   │
│   ├── booking-service/                     # ✈️ Flight & Hotel Booking (Amadeus)
│   │   ├── src/
│   │   │   ├── api/v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── flights.py           # POST /flights/search, GET /flights/{id}
│   │   │   │   │   ├── hotels.py            # POST /hotels/search, /hotels/offers
│   │   │   │   │   └── cities.py            # GET /cities (reference data)
│   │   │   │   └── router.py
│   │   │   │
│   │   │   ├── core/
│   │   │   │   ├── use_cases/
│   │   │   │   │   ├── search_flights.py    # Delegate to Amadeus client
│   │   │   │   │   └── search_hotels.py
│   │   │   │   └── entities/
│   │   │   │       ├── flight.py            # FlightEntity với business methods
│   │   │   │       └── hotel.py             # HotelEntity
│   │   │   │
│   │   │   ├── infrastructure/
│   │   │   │   └── external/
│   │   │   │       └── amadeus_client.py    # OAuth2, token caching, API calls
│   │   │   │
│   │   │   ├── schemas/
│   │   │   │   ├── flight.py                # FlightSearchRequest, FlightOffer
│   │   │   │   ├── hotel.py                 # HotelSearchRequest, HotelOffer
│   │   │   │   └── city.py                  # City reference schemas
│   │   │   │
│   │   │   ├── config/
│   │   │   │   └── settings.py              # AMADEUS_API_KEY, AMADEUS_API_SECRET
│   │   │   │
│   │   │   └── main.py
│   │   │
│   │   ├── Dockerfile
│   │   ├── requirements.txt                 # fastapi, httpx, redis
│   │   ├── .env.example
│   │   └── README.md                        # ✅ Full documentation
│   │
│   └── itinerary-service-json/              # 📅 Trip Planning (PostgreSQL)
│       ├── src/
│       │   ├── api/v1/
│       │   │   ├── endpoints/
│       │   │   │   ├── auth.py              # Local auth (duplicate with middleware)
│       │   │   │   ├── itineraries.py       # POST /, GET / (create, list)
│       │   │   │   └── activities.py        # POST /, GET /{itinerary_id}
│       │   │   ├── router.py
│       │   │   └── dependencies.py          # get_current_user, get_db
│       │   │
│       │   ├── infrastructure/
│       │   │   ├── database/
│       │   │   │   ├── connection.py        # PostgreSQL connection
│       │   │   │   └── models.py            # User, Itinerary, Activity models
│       │   │   ├── user_repo.py
│       │   │   ├── itinerary_repo.py        # create(), list_by_user()
│       │   │   └── activity_repo.py         # create(), list_by_itinerary()
│       │   │
│       │   ├── schemas/
│       │   │   ├── auth.py                  # UserRegister, UserLogin
│       │   │   ├── itinerary.py             # ItineraryCreate
│       │   │   └── activity.py              # ActivityCreate
│       │   │
│       │   ├── config/
│       │   │   └── settings.py              # DATABASE_URL (PostgreSQL)
│       │   │
│       │   ├── utils/
│       │   │   ├── security.py              # JWT, plain text password (⚠️)
│       │   │   └── json_storage.py          # JSON file I/O (unused)
│       │   │
│       │   └── main.py                      # FastAPI app, init_db()
│       │
│       ├── Dockerfile
│       ├── requirements.txt                 # fastapi, sqlalchemy, psycopg2, python-jose
│       ├── .env.example
│       └── README.md                        # ✅ Full documentation
│
├── web/                                     # 🌐 Static Web UI
│   ├── index.html                           # Main page
│   ├── styles.css                           # Styling
│   └── app.js                               # API calls to middleware
│
├── docs/                                    # 📚 Documentation
│   ├── DEPLOYMENT_AND_DEMO_GUIDE.md         # ✅ Deployment & demo guide
│   ├── RUNNING_GUIDE.md                     # Quick start guide
│   └── tai-lieu-dac-ta.md                   # Requirements spec (Vietnamese)
│
├── shared/                                  # 🔧 Shared utilities (empty - planned)
│
├── docker-compose.yml                       # 🐳 Docker orchestration
│   # Services:
│   #   - redis (cache)
│   #   - postgres (users, itineraries)
│   #   - destination-service (port 8001)
│   #   - weather-service (port 8002)
│   #   - booking-service (port 8000)
│   #   - itinerary-service (port 8000)
│   #   - middleware-service (port 9000 → exposed)
│   # Network: trip-network
│   # Volumes: redis-data, postgres-data
│
├── README.md                                # ✅ System overview & architecture
├── DEPLOYMENT_GUIDE.md                      # Deployment instructions
├── MICROSERVICE_IMPROVEMENTS.md             # Future improvements
├── PROJECT_STRUCTURE.md                     # 👈 This file
├── .gitignore
└── .env.example                             # Environment template

```

---

## 📋 Chi Tiết Các Microservices

### **1. Middleware Service** (API Gateway)

**Chức năng**:
- Single entry point cho toàn bộ hệ thống
- JWT authentication & user management
- Request routing tới downstream services
- Service discovery (static config)

**Endpoints**:
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login (returns JWT)
- `/{service}/{path...}` - Generic proxy endpoint
- Wrapper endpoints cho convenience

**Database**: PostgreSQL (users table - shared với itinerary-service)

**Port**: 9000 (external), 8000 (internal)

**Tech**: FastAPI, SQLAlchemy, httpx (proxy), python-jose (JWT)

**[📖 Documentation](./services/middleware-service/README.md)**

---

### **2. Destination Service**

**Chức năng**:
- Destination catalog management
- Search & filter destinations
- Pagination support
- Country, category, rating filters

**Endpoints**:
- `GET /api/v1/destinations` - List với pagination
- `GET /api/v1/destinations/{id}` - Get details
- `POST /api/v1/destinations/search` - Search destinations

**Database**: MySQL (destinations table)

**Port**: 8001 (internal only)

**Tech**: FastAPI, MySQL Connector Python

**[📖 Documentation](./services/destination-service/README.md)**

---

### **3. Weather Service**

**Chức năng**:
- Current weather data
- 5-day weather forecast
- Weather conditions, temperature, humidity, wind
- Response transformation

**Endpoints**:
- `GET /api/v1/weather/current/{city}` - Current weather
- `GET /api/v1/weather/forecast/{city}` - 5-day forecast

**External API**: OpenWeatherMap API

**Cache**: Redis (optional)

**Port**: 8002 (internal only)

**Tech**: FastAPI, httpx, Redis

**[📖 Documentation](./services/weather-service/README.md)**

---

### **4. Booking Service**

**Chức năng**:
- Flight search (Amadeus API)
- Hotel search (2-step: get hotel IDs → get offers)
- City/airport reference data
- OAuth2 token management với caching

**Endpoints**:
- `POST /api/v1/flights/search` - Search flights
- `GET /api/v1/flights/{offer_id}` - Get flight details
- `POST /api/v1/hotels/search` - Search hotels by city
- `POST /api/v1/hotels/offers` - Get hotel offers
- `GET /api/v1/cities` - List cities (50+ cities)

**External API**: Amadeus Test API

**Cache**: Redis (token caching)

**Port**: 8000 (internal only)

**Tech**: FastAPI, httpx, Redis

**[📖 Documentation](./services/booking-service/README.md)**

---

### **5. Itinerary Service**

**Chức năng**:
- Travel itinerary CRUD
- Activity management
- User data isolation
- Date/time scheduling

**Endpoints**:
- `POST /api/v1/auth/register` - Register (local)
- `POST /api/v1/auth/login` - Login (local)
- `POST /api/v1/itineraries` - Create itinerary
- `GET /api/v1/itineraries` - List user's itineraries
- `POST /api/v1/activities` - Add activity
- `GET /api/v1/activities/{itinerary_id}` - List activities

**Database**: PostgreSQL (itineraries, activities tables - shared users table)

**Port**: 8000 (internal only)

**Tech**: FastAPI, SQLAlchemy, psycopg2, python-jose

**Security Warning**: ⚠️ Passwords stored in plain text (development only)

**[📖 Documentation](./services/itinerary-service-json/README.md)**

---

## 🔧 Technology Stack

### **Backend**
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Architecture**: Clean Architecture, Repository Pattern
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic
- **HTTP Client**: httpx (async)
- **Authentication**: JWT (python-jose)

### **Databases**
- **PostgreSQL 15**: Users, Itineraries, Activities
- **MySQL**: Destinations catalog
- **Redis 7**: Cache cho Booking & Weather

### **Infrastructure**
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Network**: Docker bridge network (trip-network)
- **Service Discovery**: Static configuration (environment variables)

### **External APIs**
- **Amadeus Test API**: Flight & Hotel search
- **OpenWeatherMap API**: Weather forecasting

### **Frontend**
- **Web UI**: Static HTML/CSS/JavaScript
- **Server**: Python http.server (development)

---

## 🚀 Deployment Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Docker Network                         │
│                    (trip-network)                         │
│                                                           │
│  ┌────────────────────────────────────────┐             │
│  │     Middleware Service (9000)          │             │
│  │     ← Only Exposed Service            │             │
│  └──┬────┬────┬────┬────┬────────────────┘             │
│     │    │    │    │    │                               │
│     ↓    ↓    ↓    ↓    ↓                               │
│  ┌────┐┌────┐┌────┐┌────┐┌────┐                       │
│  │Dest││Wea ││Book││Itin││DB  │                       │
│  │8001││8002││8000││8000││    │                       │
│  └────┘└────┘└────┘└────┘│    │                       │
│                           │Post│                       │
│                           │gres│                       │
│                           │SQL │                       │
│                           │5432│                       │
│                           └────┘                       │
│                           ┌────┐                       │
│                           │MySQL                      │
│                           │3306│                       │
│                           └────┘                       │
│                           ┌────┐                       │
│                           │Redis                      │
│                           │6379│                       │
│                           └────┘                       │
└───────────────────────────────────────────────────────────┘
          ↑
          │ HTTP Requests
          │
    ┌─────────────┐
    │   Client    │
    │ (Web/cURL)  │
    └─────────────┘
```

### **Network Isolation**
- **External**: Chỉ Middleware Service expose port 9000
- **Internal**: Tất cả services giao tiếp trong Docker network
- **Service Discovery**: Docker DNS (service names → IP)

### **Data Flow**
1. Client → Middleware (JWT auth)
2. Middleware validates JWT
3. Middleware proxy request → Downstream service
4. Downstream service process request
5. Response → Middleware → Client

---

## 📝 Environment Variables

Mỗi service cần file `.env` với cấu hình riêng:

### **Middleware Service**
```bash
DATABASE_URL=postgresql+psycopg2://trip:trip@postgres:5432/trip_hub
DESTINATION_SERVICE_URL=http://destination-service:8001
WEATHER_SERVICE_URL=http://weather-service:8002
ITINERARY_SERVICE_URL=http://itinerary-service:8000
BOOKING_SERVICE_URL=http://booking-service:8000
```

### **Booking Service**
```bash
AMADEUS_API_KEY=your-key-here
AMADEUS_API_SECRET=your-secret-here
AMADEUS_BASE_URL=https://test.api.amadeus.com
REDIS_HOST=redis
REDIS_PORT=6379
```

### **Weather Service**
```bash
OPENWEATHER_API_KEY=your-key-here
REDIS_URL=redis://redis:6379/0
```

### **Destination Service**
```bash
DATABASE_URL=mysql://root:root@mysql:3306/destinations
```

### **Itinerary Service**
```bash
DATABASE_URL=postgresql+psycopg2://trip:trip@postgres:5432/trip_hub
```

---

## 🚦 Quick Start

### **1. Clone Repository**
```bash
git clone <repository-url>
cd trip-hub
```

### **2. Configure Environment**
```bash
# Copy env files
cp services/middleware-service/.env.example services/middleware-service/.env
cp services/booking-service/.env.example services/booking-service/.env
cp services/weather-service/.env.example services/weather-service/.env

# Edit .env files với actual API keys
```

### **3. Start Services**
```bash
# Build và start tất cả services
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f middleware-service
```

### **4. Verify Health**
```bash
# Check API Gateway
curl http://localhost:9000/health

# Expected: {"status": "ok", "service": "middleware-service", ...}
```

### **5. Test API**
```bash
# Register user
curl -X POST http://localhost:9000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# Login
TOKEN=$(curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}' \
  | jq -r '.access_token')

# List destinations
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:9000/api/v1/destination/destinations
```

### **6. Access Web UI**
```bash
cd web
python -m http.server 8080
# Open: http://localhost:8080
# Set API URL: http://localhost:9000
```

---

## 📊 Service Dependencies

```
middleware-service
├── Depends on: postgres
└── Routes to:
    ├── destination-service
    ├── weather-service
    ├── booking-service
    └── itinerary-service

destination-service
└── Depends on: mysql (not in docker-compose)

weather-service
└── Depends on: redis, OpenWeatherMap API

booking-service
└── Depends on: redis, Amadeus API

itinerary-service
└── Depends on: postgres (shared)
```

---

## 🔐 Security Notes

### **Current Implementation (Development)**
- ⚠️ **Plain text passwords** trong itinerary-service
- ⚠️ **Hardcoded JWT secret** ("SECRET")
- ✅ JWT authentication qua middleware
- ✅ User data isolation
- ✅ CORS enabled

### **Production Requirements**
- Implement bcrypt/argon2 password hashing
- Use environment variables cho JWT secret
- Add HTTPS/TLS
- Implement rate limiting
- Add API key rotation
- Secrets management (Vault, AWS Secrets Manager)

---

## 📚 Documentation

### **Service-Level Documentation**
- [Middleware Service README](./services/middleware-service/README.md) - ✅ 1017 lines
- [Destination Service README](./services/destination-service/README.md) - ✅ 611 lines
- [Weather Service README](./services/weather-service/README.md) - ✅ 659 lines
- [Booking Service README](./services/booking-service/README.md) - ✅ 1392 lines
- [Itinerary Service README](./services/itinerary-service-json/README.md) - ✅ 1292 lines

### **System-Level Documentation**
- [System README](./README.md) - ✅ System overview & architecture
- [Deployment & Demo Guide](./docs/DEPLOYMENT_AND_DEMO_GUIDE.md) - ✅ Complete guide
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Production deployment
- [Microservice Improvements](./MICROSERVICE_IMPROVEMENTS.md) - Future enhancements
- [Project Structure](./PROJECT_STRUCTURE.md) - 👈 This document

---

## 🎯 Development Workflow

1. **Service Development**: Mỗi service có thể develop độc lập
2. **Local Testing**: Use Docker Compose cho integration testing
3. **API Gateway**: Tất cả requests qua Middleware (port 9000)
4. **Service Communication**: HTTP/REST qua Docker network
5. **Database**: Service-specific databases (PostgreSQL, MySQL)
6. **Caching**: Redis cho external API responses

---

## 📈 Scalability Considerations

### **Current Architecture**
- **Stateless Services**: Dễ scale horizontally
- **Database Per Service**: Independent scaling
- **Shared Database**: Users table shared (trade-off)
- **No Load Balancer**: Single middleware instance

### **Future Improvements**
- Kubernetes deployment với HPA
- Database replication & sharding
- Redis cluster cho high availability
- Message queue cho async communication
- Service mesh (Istio) cho advanced routing
- API rate limiting
- Centralized logging (ELK)
- Distributed tracing (Jaeger)

---

## 🧪 Testing

### **Planned** (Not Implemented)
- Unit tests cho mỗi service
- Integration tests
- E2E tests với Docker Compose
- Load testing (Locust/k6)
- Contract testing giữa services

---

## 📦 Dependencies Summary

### **Common Dependencies**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
```

### **Service-Specific**
- **Middleware**: sqlalchemy, httpx, python-jose
- **Destination**: mysql-connector-python
- **Weather**: httpx, redis (optional)
- **Booking**: httpx, redis
- **Itinerary**: sqlalchemy, psycopg2-binary, python-jose

---

## 🔄 Git Workflow

```
.gitignore              # Python, Docker, IDE files
├── __pycache__/
├── *.pyc
├── .env
├── .venv/
├── logs/
└── docker volumes
```

---

## 🏗️ Project Status

**Status**: ✅ **Development Complete**

**Completed**:
- ✅ 5 microservices implemented
- ✅ API Gateway pattern
- ✅ JWT authentication
- ✅ Docker Compose deployment
- ✅ Comprehensive documentation
- ✅ Web UI demo
- ✅ External API integration (Amadeus, OpenWeatherMap)

**Production Readiness**: ⚠️ **Security improvements needed**
- Plain text passwords → bcrypt/argon2
- Hardcoded secrets → environment variables
- Add HTTPS/TLS
- Add rate limiting
- Add monitoring & logging

---

**Last Updated**: December 2024  
**Maintainer**: Trip Hub Development Team
