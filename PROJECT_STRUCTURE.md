# 📁 Cấu Trúc Dự Án Trip Hub - Travel Planning Application

## 🎯 Tổng Quan
Ứng dụng lập kế hoạch du lịch với kiến trúc microservices, sử dụng FastAPI, Clean Architecture, Docker và Message Broker.

## 🧱 Cấu Trúc Thư Mục

```
trip-hub/
├── services/                                    # Các microservices
│   ├── user-service/                           # Service quản lý người dùng
│   │   ├── src/
│   │   │   ├── api/                           # API Layer (Controllers)
│   │   │   │   ├── v1/
│   │   │   │   │   ├── endpoints/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── auth.py           # Đăng nhập, đăng ký
│   │   │   │   │   │   ├── users.py          # CRUD người dùng
│   │   │   │   │   │   └── profile.py        # Quản lý profile
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── router.py             # Tổng hợp routes
│   │   │   │   └── dependencies.py            # FastAPI dependencies
│   │   │   │
│   │   │   ├── core/                          # Application Core (Use Cases)
│   │   │   │   ├── use_cases/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── register_user.py
│   │   │   │   │   ├── authenticate_user.py
│   │   │   │   │   ├── update_profile.py
│   │   │   │   │   └── get_user_info.py
│   │   │   │   ├── entities/                  # Domain Entities
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── user.py
│   │   │   │   └── interfaces/                # Repository Interfaces
│   │   │   │       ├── __init__.py
│   │   │   │       └── user_repository.py
│   │   │   │
│   │   │   ├── infrastructure/                # Infrastructure Layer
│   │   │   │   ├── database/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── connection.py         # DB connection
│   │   │   │   │   ├── models.py             # SQLAlchemy models
│   │   │   │   │   └── repositories/
│   │   │   │   │       ├── __init__.py
│   │   │   │   │       └── user_repository_impl.py
│   │   │   │   ├── messaging/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── publisher.py          # Message publisher
│   │   │   │   │   └── consumer.py           # Message consumer
│   │   │   │   ├── cache/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── redis_client.py
│   │   │   │   └── external/
│   │   │   │       ├── __init__.py
│   │   │   │       └── email_service.py
│   │   │   │
│   │   │   ├── config/                        # Configuration
│   │   │   │   ├── __init__.py
│   │   │   │   ├── settings.py               # Pydantic settings
│   │   │   │   └── logging.py
│   │   │   │
│   │   │   ├── schemas/                       # Pydantic schemas (DTOs)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py
│   │   │   │   ├── auth.py
│   │   │   │   └── response.py
│   │   │   │
│   │   │   ├── utils/                         # Utilities
│   │   │   │   ├── __init__.py
│   │   │   │   ├── security.py               # JWT, password hashing
│   │   │   │   ├── validators.py
│   │   │   │   └── exceptions.py
│   │   │   │
│   │   │   └── main.py                        # FastAPI app entry point
│   │   │
│   │   ├── tests/                             # Tests
│   │   │   ├── unit/
│   │   │   │   ├── test_use_cases.py
│   │   │   │   └── test_entities.py
│   │   │   ├── integration/
│   │   │   │   ├── test_api.py
│   │   │   │   └── test_repository.py
│   │   │   └── conftest.py
│   │   │
│   │   ├── migrations/                        # Alembic migrations
│   │   │   ├── versions/
│   │   │   ├── env.py
│   │   │   └── script.py.mako
│   │   │
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── requirements-dev.txt
│   │   ├── .env.example
│   │   ├── alembic.ini
│   │   └── README.md
│   │
│   ├── destination-service/                    # Service quản lý điểm đến
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── v1/
│   │   │   │   │   ├── endpoints/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── destinations.py   # CRUD điểm đến
│   │   │   │   │   │   ├── attractions.py    # Địa điểm tham quan
│   │   │   │   │   │   ├── hotels.py         # Khách sạn
│   │   │   │   │   │   └── search.py         # Tìm kiếm
│   │   │   │   │   └── router.py
│   │   │   │   └── dependencies.py
│   │   │   │
│   │   │   ├── core/
│   │   │   │   ├── use_cases/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── get_destination_info.py
│   │   │   │   │   ├── search_destinations.py
│   │   │   │   │   ├── get_attractions.py
│   │   │   │   │   └── get_nearby_hotels.py
│   │   │   │   ├── entities/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── destination.py
│   │   │   │   │   ├── attraction.py
│   │   │   │   │   └── hotel.py
│   │   │   │   └── interfaces/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── destination_repository.py
│   │   │   │       └── external_api_client.py
│   │   │   │
│   │   │   ├── infrastructure/
│   │   │   │   ├── database/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── connection.py
│   │   │   │   │   ├── models.py
│   │   │   │   │   └── repositories/
│   │   │   │   │       ├── __init__.py
│   │   │   │   │       ├── destination_repository_impl.py
│   │   │   │   │       └── attraction_repository_impl.py
│   │   │   │   ├── messaging/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── publisher.py
│   │   │   │   │   └── consumer.py
│   │   │   │   ├── cache/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── redis_client.py
│   │   │   │   └── external/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── google_places_client.py
│   │   │   │       └── tripadvisor_client.py
│   │   │   │
│   │   │   ├── config/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── settings.py
│   │   │   │   └── logging.py
│   │   │   │
│   │   │   ├── schemas/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── destination.py
│   │   │   │   ├── attraction.py
│   │   │   │   └── hotel.py
│   │   │   │
│   │   │   ├── utils/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── validators.py
│   │   │   │   └── exceptions.py
│   │   │   │
│   │   │   └── main.py
│   │   │
│   │   ├── tests/
│   │   ├── migrations/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── requirements-dev.txt
│   │   ├── .env.example
│   │   └── README.md
│   │
│   ├── itinerary-service/                      # Service lên lịch trình
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── v1/
│   │   │   │   │   ├── endpoints/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── itineraries.py    # CRUD lịch trình
│   │   │   │   │   │   ├── activities.py     # Hoạt động trong lịch trình
│   │   │   │   │   │   └── suggestions.py    # Gợi ý lịch trình
│   │   │   │   │   └── router.py
│   │   │   │   └── dependencies.py
│   │   │   │
│   │   │   ├── core/
│   │   │   │   ├── use_cases/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── create_itinerary.py
│   │   │   │   │   ├── generate_schedule.py  # Tự động lên lịch
│   │   │   │   │   ├── add_activity.py
│   │   │   │   │   ├── optimize_route.py     # Tối ưu lộ trình
│   │   │   │   │   └── share_itinerary.py
│   │   │   │   ├── entities/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── itinerary.py
│   │   │   │   │   └── activity.py
│   │   │   │   └── interfaces/
│   │   │   │       ├── __init__.py
│   │   │   │       └── itinerary_repository.py
│   │   │   │
│   │   │   ├── infrastructure/
│   │   │   │   ├── database/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── connection.py
│   │   │   │   │   ├── models.py
│   │   │   │   │   └── repositories/
│   │   │   │   │       ├── __init__.py
│   │   │   │   │       └── itinerary_repository_impl.py
│   │   │   │   ├── messaging/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── publisher.py
│   │   │   │   │   └── consumer.py
│   │   │   │   ├── cache/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── redis_client.py
│   │   │   │   └── external/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── destination_service_client.py
│   │   │   │       └── weather_service_client.py
│   │   │   │
│   │   │   ├── config/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── settings.py
│   │   │   │   └── logging.py
│   │   │   │
│   │   │   ├── schemas/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── itinerary.py
│   │   │   │   └── activity.py
│   │   │   │
│   │   │   ├── utils/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schedule_optimizer.py     # Thuật toán tối ưu
│   │   │   │   ├── validators.py
│   │   │   │   └── exceptions.py
│   │   │   │
│   │   │   └── main.py
│   │   │
│   │   ├── tests/
│   │   ├── migrations/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── requirements-dev.txt
│   │   ├── .env.example
│   │   └── README.md
│   │
│   ├── booking-service/                        # Service đặt vé, phòng
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── v1/
│   │   │   │   │   ├── endpoints/
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── flights.py        # Tìm kiếm, đặt vé máy bay
│   │   │   │   │   │   ├── hotels.py         # Tìm kiếm, đặt phòng
│   │   │   │   │   │   ├── bookings.py       # Quản lý booking
│   │   │   │   │   │   └── payments.py       # Xử lý thanh toán
│   │   │   │   │   └── router.py
│   │   │   │   └── dependencies.py
│   │   │   │
│   │   │   ├── core/
│   │   │   │   ├── use_cases/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── search_flights.py
│   │   │   │   │   ├── book_flight.py
│   │   │   │   │   ├── search_hotels.py
│   │   │   │   │   ├── book_hotel.py
│   │   │   │   │   ├── process_payment.py
│   │   │   │   │   └── cancel_booking.py
│   │   │   │   ├── entities/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── booking.py
│   │   │   │   │   ├── flight.py
│   │   │   │   │   ├── hotel_booking.py
│   │   │   │   │   └── payment.py
│   │   │   │   └── interfaces/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── booking_repository.py
│   │   │   │       └── payment_gateway.py
│   │   │   │
│   │   │   ├── infrastructure/
│   │   │   │   ├── database/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── connection.py
│   │   │   │   │   ├── models.py
│   │   │   │   │   └── repositories/
│   │   │   │   │       ├── __init__.py
│   │   │   │   │       └── booking_repository_impl.py
│   │   │   │   ├── messaging/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── publisher.py
│   │   │   │   │   └── consumer.py
│   │   │   │   ├── cache/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── redis_client.py
│   │   │   │   └── external/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── flight_api_client.py  # API đặt vé máy bay
│   │   │   │       ├── hotel_api_client.py   # API đặt phòng
│   │   │   │       └── payment_gateway_client.py
│   │   │   │
│   │   │   ├── config/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── settings.py
│   │   │   │   └── logging.py
│   │   │   │
│   │   │   ├── schemas/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── booking.py
│   │   │   │   ├── flight.py
│   │   │   │   ├── hotel.py
│   │   │   │   └── payment.py
│   │   │   │
│   │   │   ├── utils/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── validators.py
│   │   │   │   └── exceptions.py
│   │   │   │
│   │   │   └── main.py
│   │   │
│   │   ├── tests/
│   │   ├── migrations/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── requirements-dev.txt
│   │   ├── .env.example
│   │   └── README.md
│   │
│   └── weather-service/                        # Service thông tin thời tiết
│       ├── src/
│       │   ├── api/
│       │   │   ├── v1/
│       │   │   │   ├── endpoints/
│       │   │   │   │   ├── __init__.py
│       │   │   │   │   ├── weather.py        # Dự báo thời tiết
│       │   │   │   │   └── forecast.py       # Dự báo nhiều ngày
│       │   │   │   └── router.py
│       │   │   └── dependencies.py
│       │   │
│       │   ├── core/
│       │   │   ├── use_cases/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── get_current_weather.py
│       │   │   │   └── get_forecast.py
│       │   │   ├── entities/
│       │   │   │   ├── __init__.py
│       │   │   │   └── weather.py
│       │   │   └── interfaces/
│       │   │       ├── __init__.py
│       │   │       └── weather_repository.py
│       │   │
│       │   ├── infrastructure/
│       │   │   ├── database/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── connection.py
│       │   │   │   ├── models.py
│       │   │   │   └── repositories/
│       │   │   │       ├── __init__.py
│       │   │   │       └── weather_repository_impl.py
│       │   │   ├── messaging/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── publisher.py
│       │   │   │   └── consumer.py
│       │   │   ├── cache/
│       │   │   │   ├── __init__.py
│       │   │   │   └── redis_client.py
│       │   │   └── external/
│       │   │       ├── __init__.py
│       │   │       └── openweather_client.py  # OpenWeather API
│       │   │
│       │   ├── config/
│       │   │   ├── __init__.py
│       │   │   ├── settings.py
│       │   │   └── logging.py
│       │   │
│       │   ├── schemas/
│       │   │   ├── __init__.py
│       │   │   └── weather.py
│       │   │
│       │   ├── utils/
│       │   │   ├── __init__.py
│       │   │   ├── validators.py
│       │   │   └── exceptions.py
│       │   │
│       │   └── main.py
│       │
│       ├── tests/
│       ├── migrations/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── requirements-dev.txt
│       ├── .env.example
│       └── README.md
│
├── shared/                                      # Thư viện dùng chung
│   ├── libs/                                   # Common utilities
│   │   ├── logging/
│   │   │   ├── __init__.py
│   │   │   └── logger.py                      # Centralized logging
│   │   ├── tracing/
│   │   │   ├── __init__.py
│   │   │   └── tracer.py                      # Distributed tracing
│   │   ├── monitoring/
│   │   │   ├── __init__.py
│   │   │   └── metrics.py                     # Prometheus metrics
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   └── jwt_handler.py                 # JWT utilities
│   │   └── database/
│   │       ├── __init__.py
│   │       └── base.py                        # Base repository
│   │
│   └── contracts/                              # Event schemas, message contracts
│       ├── __init__.py
│       ├── events/
│       │   ├── __init__.py
│       │   ├── user_events.py                 # User domain events
│       │   ├── booking_events.py              # Booking domain events
│       │   └── itinerary_events.py            # Itinerary domain events
│       └── schemas/
│           ├── __init__.py
│           └── common.py                      # Common schemas
│
├── api-gateway/                                 # API Gateway (Kong/Nginx)
│   ├── kong/
│   │   ├── kong.yml                           # Kong configuration
│   │   └── plugins/
│   │       ├── rate-limiting.yml
│   │       ├── jwt-auth.yml
│   │       └── cors.yml
│   └── nginx/
│       ├── nginx.conf
│       └── conf.d/
│           └── default.conf
│
├── docker/                                      # Docker artifacts
│   ├── base.Dockerfile                         # Base image cho Python services
│   ├── docker-compose.yml                      # Production compose
│   ├── docker-compose.local.yml                # Local development
│   ├── docker-compose.test.yml                 # Testing environment
│   └── .env.example                            # Environment variables template
│
├── infrastructure/                              # Infrastructure as Code
│   ├── kubernetes/                             # K8s manifests
│   │   ├── namespaces/
│   │   │   ├── dev.yaml
│   │   │   ├── staging.yaml
│   │   │   └── production.yaml
│   │   ├── services/
│   │   │   ├── user-service/
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── service.yaml
│   │   │   │   ├── configmap.yaml
│   │   │   │   └── hpa.yaml                   # Horizontal Pod Autoscaler
│   │   │   ├── destination-service/
│   │   │   ├── itinerary-service/
│   │   │   ├── booking-service/
│   │   │   └── weather-service/
│   │   ├── ingress/
│   │   │   └── ingress.yaml
│   │   ├── monitoring/
│   │   │   ├── prometheus.yaml
│   │   │   └── grafana.yaml
│   │   └── databases/
│   │       ├── postgres.yaml
│   │       ├── redis.yaml
│   │       └── rabbitmq.yaml
│   │
│   └── terraform/                              # Terraform IaC
│       ├── modules/
│       │   ├── vpc/
│       │   ├── eks/
│       │   └── rds/
│       ├── environments/
│       │   ├── dev/
│       │   ├── staging/
│       │   └── production/
│       └── main.tf
│
├── ci-cd/                                       # CI/CD pipelines
│   ├── github-actions/
│   │   ├── build-and-test.yml
│   │   ├── deploy-dev.yml
│   │   ├── deploy-staging.yml
│   │   └── deploy-production.yml
│   ├── gitlab-ci/
│   │   └── .gitlab-ci.yml
│   └── jenkins/
│       └── Jenkinsfile
│
├── monitoring/                                  # Monitoring & Observability
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── alerts/
│   │       ├── service-alerts.yml
│   │       └── infrastructure-alerts.yml
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   ├── service-metrics.json
│   │   │   ├── business-metrics.json
│   │   │   └── infrastructure.json
│   │   └── provisioning/
│   │       ├── datasources.yml
│   │       └── dashboards.yml
│   └── elk/                                     # ELK Stack
│       ├── elasticsearch.yml
│       ├── logstash/
│       │   └── pipeline.conf
│       └── kibana.yml
│
├── scripts/                                     # Utility scripts
│   ├── setup/
│   │   ├── init-dev-env.sh                    # Setup development environment
│   │   └── install-dependencies.sh
│   ├── database/
│   │   ├── backup.sh
│   │   ├── restore.sh
│   │   └── migrate-all.sh
│   ├── deployment/
│   │   ├── deploy.sh
│   │   └── rollback.sh
│   └── testing/
│       ├── run-integration-tests.sh
│       └── run-e2e-tests.sh
│
├── docs/                                        # Documentation
│   ├── architecture/
│   │   ├── system-design.md
│   │   ├── microservices-communication.md
│   │   └── database-schema.md
│   ├── api/
│   │   ├── user-service-api.md
│   │   ├── destination-service-api.md
│   │   ├── itinerary-service-api.md
│   │   ├── booking-service-api.md
│   │   └── weather-service-api.md
│   ├── deployment/
│   │   ├── local-setup.md
│   │   ├── kubernetes-deployment.md
│   │   └── production-checklist.md
│   └── development/
│       ├── coding-standards.md
│       ├── git-workflow.md
│       └── testing-guidelines.md
│
├── tests/                                       # End-to-end tests
│   ├── e2e/
│   │   ├── test_user_journey.py
│   │   ├── test_booking_flow.py
│   │   └── test_itinerary_creation.py
│   ├── integration/
│   │   └── test_service_communication.py
│   └── performance/
│       └── load_tests.py
│
├── .github/                                     # GitHub specific
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
│
├── .gitignore
├── README.md                                    # Project overview
├── CONTRIBUTING.md
├── LICENSE
└── Makefile                                     # Common commands
```

## 📋 Mô Tả Các Microservices

### 1. **user-service**
- Quản lý người dùng, authentication, authorization
- JWT token generation và validation
- Profile management

### 2. **destination-service**
- Quản lý thông tin điểm đến du lịch
- Tích hợp Google Places API, TripAdvisor API
- Thông tin về địa điểm tham quan, khách sạn
- Search và filter destinations

### 3. **itinerary-service**
- Tạo và quản lý lịch trình du lịch
- Tự động lên lịch dựa trên thời gian và địa điểm
- Tối ưu hóa lộ trình di chuyển
- Chia sẻ lịch trình với bạn bè

### 4. **booking-service**
- Tìm kiếm và đặt vé máy bay
- Tìm kiếm và đặt phòng khách sạn
- Xử lý thanh toán
- Quản lý bookings

### 5. **weather-service**
- Cung cấp thông tin thời tiết hiện tại
- Dự báo thời tiết nhiều ngày
- Tích hợp OpenWeather API
- Cache dữ liệu để tối ưu performance

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Architecture**: Clean Architecture
- **ORM**: SQLAlchemy
- **Migration**: Alembic
- **Validation**: Pydantic

### Database
- **Primary DB**: PostgreSQL
- **Cache**: Redis
- **Message Broker**: RabbitMQ / Apache Kafka

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **API Gateway**: Kong / Nginx
- **Service Mesh**: Istio (optional)

### Monitoring & Logging
- **Metrics**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger / OpenTelemetry
- **APM**: New Relic / DataDog (optional)

### CI/CD
- **Version Control**: Git
- **CI/CD**: GitHub Actions / GitLab CI
- **IaC**: Terraform
- **Container Registry**: Docker Hub / AWS ECR

## 🚀 Quick Start

```bash
# Clone repository
git clone <repository-url>
cd trip-hub

# Setup local environment
make setup

# Start all services
make up

# Run tests
make test

# View logs
make logs
```

## 📝 Development Workflow

1. Mỗi service có thể phát triển độc lập
2. Sử dụng Docker Compose cho local development
3. API Gateway làm entry point cho tất cả requests
4. Services giao tiếp qua REST API và Message Broker
5. Shared libraries để tránh code duplication

## 🔐 Security

- JWT authentication
- API rate limiting
- CORS configuration
- Input validation
- SQL injection prevention
- Secrets management (Vault/AWS Secrets Manager)

## 📊 Scalability

- Horizontal scaling với Kubernetes HPA
- Database replication và sharding
- Redis caching layer
- CDN cho static assets
- Load balancing với API Gateway
