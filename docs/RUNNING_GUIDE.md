# Trip Hub - Running Guide

## Tech stack
- Docker + Docker Compose
- FastAPI services (Python)
- PostgreSQL 15
- Redis 7
- Static web UI (HTML/CSS/JS)

## Services
- `middleware-service`: API gateway + auth (JWT). Exposes `http://localhost:9000`.
- `destination-service`: destination search (internal).
- `weather-service`: weather API proxy (internal).
- `itinerary-service`: itineraries + activities (internal, uses Postgres).
- `booking-service`: flights/hotels/cities (internal, calls external APIs).
- `postgres`: primary database for users + itinerary data.
- `redis`: cache for booking/weather.

## Local run (Docker)
From repo root:
```bash
docker compose up -d --build
```

Check health:
```bash
curl http://localhost:9000/health
```

Stop:
```bash
docker compose down
```

## Web UI
Serve the `web/` folder:
```bash
cd web
python -m http.server 8080
```

Open:
```
http://localhost:8080
```

Set Base URL to:
```
http://localhost:9000
```

## Authentication (via middleware)
- Register: `POST /api/v1/auth/register`
- Login: `POST /api/v1/auth/login`
- Use the returned JWT in `Authorization: Bearer <token>`

## API routing (via middleware)
Middleware forwards requests using:
```
/api/v1/{service}/{path...}
```

Services:
- `destination`
- `weather`
- `itinerary`
- `booking`

Example:
```
GET /api/v1/destination/destinations?query=paris
```

## Itinerary service
Base (via middleware):
```
/api/v1/itinerary
```

Endpoints:
- `POST /itineraries`
- `GET /itineraries`
- `POST /activities`
- `GET /activities/{itinerary_id}`

## Booking service
Base (via middleware):
```
/api/v1/booking
```

Endpoints:
- `GET /cities?keyword=...&country_code=...&limit=...`
- `POST /flights/search`
- `GET /flights/{offer_id}`
- `POST /hotels/search`
- `POST /hotels/offers`

## Weather service
Base (via middleware):
```
/api/v1/weather
```

Endpoint:
- `GET /current?location=Paris`

## Database
Postgres is used for:
- middleware users
- itinerary data (itineraries + activities)

Default DB config (Docker):
- user: `trip`
- password: `trip`
- database: `trip_hub`

## Notes
- If you rebuild without a DB dump, Postgres will be empty.
- To persist or share data, export with `pg_dump` and import on another machine.
