from fastapi import APIRouter
from src.core.bootstrap import service_router

router = APIRouter()


@router.get("/services", tags=["info"])
async def list_services():
    """
    Liệt kê tất cả các backend services và APIs của chúng.
    Hiển thị đầy đủ endpoints, methods, và ví dụ request/response.
    """
    return {
        "total_services": len(service_router.available_services()),
        "services": {
            "destination": {
                "name": "Destination Service",
                "description": "Quản lý thông tin điểm đến du lịch",
                "base_url": "http://localhost:8001",
                "via_middleware": "http://localhost:9000/api/v1/destination",
                "apis": [
                    {
                        "endpoint": "/api/v1/destinations",
                        "method": "GET",
                        "description": "Lấy danh sách tất cả điểm đến",
                        "via_middleware": "/api/v1/destination/destinations",
                        "example_request": {
                            "method": "GET",
                            "url": "http://localhost:9000/api/v1/destination/destinations"
                        },
                        "example_response": {
                            "destinations": [
                                {
                                    "id": 1,
                                    "name": "Ha Noi",
                                    "description": "Capital of Vietnam",
                                    "country": "Vietnam"
                                }
                            ]
                        }
                    },
                    {
                        "endpoint": "/api/v1/destinations/{id}",
                        "method": "GET",
                        "description": "Lấy thông tin chi tiết một điểm đến",
                        "via_middleware": "/api/v1/destination/destinations/1",
                        "example_request": {
                            "method": "GET",
                            "url": "http://localhost:9000/api/v1/destination/destinations/1"
                        }
                    },
                    {
                        "endpoint": "/api/v1/destinations",
                        "method": "POST",
                        "description": "Tạo điểm đến mới",
                        "via_middleware": "/api/v1/destination/destinations",
                        "example_request": {
                            "method": "POST",
                            "url": "http://localhost:9000/api/v1/destination/destinations",
                            "body": {
                                "name": "Da Nang",
                                "description": "Central coast city",
                                "country": "Vietnam"
                            }
                        }
                    }
                ]
            },
            "weather": {
                "name": "Weather Service",
                "description": "Cung cấp thông tin thời tiết theo địa điểm",
                "base_url": "http://localhost:8004",
                "via_middleware": "http://localhost:9000/api/v1/weather",
                "apis": [
                    {
                        "endpoint": "/api/v1/weather/forecast",
                        "method": "GET",
                        "description": "Lấy dự báo thời tiết theo thành phố",
                        "via_middleware": "/api/v1/weather/forecast",
                        "parameters": {
                            "city": "Tên thành phố (required)"
                        },
                        "example_request": {
                            "method": "GET",
                            "url": "http://localhost:9000/api/v1/weather/forecast?city=hanoi"
                        },
                        "example_response": {
                            "city": "Hanoi",
                            "temperature": 28,
                            "condition": "Sunny",
                            "humidity": 65
                        }
                    },
                    {
                        "endpoint": "/api/v1/weather/current",
                        "method": "GET",
                        "description": "Lấy thời tiết hiện tại",
                        "via_middleware": "/api/v1/weather/current",
                        "parameters": {
                            "city": "Tên thành phố",
                            "lat": "Latitude (optional)",
                            "lon": "Longitude (optional)"
                        },
                        "example_request": {
                            "method": "GET",
                            "url": "http://localhost:9000/api/v1/weather/current?city=saigon"
                        }
                    }
                ]
            },
            "booking": {
                "name": "Booking Service",
                "description": "Tìm kiếm và đặt vé máy bay, khách sạn",
                "base_url": "http://localhost:8003",
                "via_middleware": "http://localhost:9000/api/v1/booking",
                "apis": [
                    {
                        "endpoint": "/api/v1/flights/search",
                        "method": "POST",
                        "description": "Tìm kiếm chuyến bay",
                        "via_middleware": "/api/v1/booking/flights/search",
                        "example_request": {
                            "method": "POST",
                            "url": "http://localhost:9000/api/v1/booking/flights/search",
                            "body": {
                                "origin": "HAN",
                                "destination": "SGN",
                                "departure_date": "2024-12-30",
                                "adults": 1
                            }
                        },
                        "example_response": {
                            "flights": [
                                {
                                    "id": "VN123",
                                    "airline": "Vietnam Airlines",
                                    "departure": "09:00",
                                    "arrival": "11:00",
                                    "price": 1500000
                                }
                            ]
                        }
                    },
                    {
                        "endpoint": "/api/v1/hotels/search",
                        "method": "POST",
                        "description": "Tìm kiếm khách sạn",
                        "via_middleware": "/api/v1/booking/hotels/search",
                        "example_request": {
                            "method": "POST",
                            "url": "http://localhost:9000/api/v1/booking/hotels/search",
                            "body": {
                                "city_code": "HAN",
                                "check_in": "2024-12-25",
                                "check_out": "2024-12-27",
                                "adults": 2
                            }
                        },
                        "example_response": {
                            "hotels": [
                                {
                                    "name": "Hanoi Hotel",
                                    "rating": 4.5,
                                    "price_per_night": 800000,
                                    "amenities": ["WiFi", "Pool", "Breakfast"]
                                }
                            ]
                        }
                    },
                    {
                        "endpoint": "/api/v1/bookings",
                        "method": "GET",
                        "description": "Lấy danh sách booking",
                        "via_middleware": "/api/v1/booking/bookings",
                        "example_request": {
                            "method": "GET",
                            "url": "http://localhost:9000/api/v1/booking/bookings"
                        }
                    },
                    {
                        "endpoint": "/api/v1/bookings",
                        "method": "POST",
                        "description": "Tạo booking mới",
                        "via_middleware": "/api/v1/booking/bookings",
                        "example_request": {
                            "method": "POST",
                            "url": "http://localhost:9000/api/v1/booking/bookings",
                            "body": {
                                "type": "flight",
                                "flight_id": "VN123",
                                "passenger_name": "Nguyen Van A"
                            }
                        }
                    }
                ]
            },
            "itinerary": {
                "name": "Itinerary Service",
                "description": "Quản lý lịch trình du lịch cá nhân",
                "base_url": "http://localhost:8002",
                "via_middleware": "http://localhost:9000/api/v1/itinerary",
                "apis": [
                    {
                        "endpoint": "/api/v1/itineraries",
                        "method": "GET",
                        "description": "Lấy danh sách lịch trình",
                        "via_middleware": "/api/v1/itinerary/itineraries",
                        "example_request": {
                            "method": "GET",
                            "url": "http://localhost:9000/api/v1/itinerary/itineraries"
                        },
                        "example_response": {
                            "itineraries": [
                                {
                                    "id": 1,
                                    "title": "Ha Noi 3 ngay 2 dem",
                                    "start_date": "2024-12-25",
                                    "end_date": "2024-12-27",
                                    "destinations": ["Hanoi", "Ha Long Bay"]
                                }
                            ]
                        }
                    },
                    {
                        "endpoint": "/api/v1/itineraries",
                        "method": "POST",
                        "description": "Tạo lịch trình mới",
                        "via_middleware": "/api/v1/itinerary/itineraries",
                        "example_request": {
                            "method": "POST",
                            "url": "http://localhost:9000/api/v1/itinerary/itineraries",
                            "body": {
                                "title": "Sai Gon City Tour",
                                "start_date": "2025-01-10",
                                "end_date": "2025-01-12",
                                "description": "Explore Saigon in 3 days"
                            }
                        }
                    },
                    {
                        "endpoint": "/api/v1/itineraries/{id}",
                        "method": "GET",
                        "description": "Lấy chi tiết lịch trình",
                        "via_middleware": "/api/v1/itinerary/itineraries/1",
                        "example_request": {
                            "method": "GET",
                            "url": "http://localhost:9000/api/v1/itinerary/itineraries/1"
                        }
                    },
                    {
                        "endpoint": "/api/v1/itineraries/{id}",
                        "method": "PUT",
                        "description": "Cập nhật lịch trình",
                        "via_middleware": "/api/v1/itinerary/itineraries/1",
                        "example_request": {
                            "method": "PUT",
                            "url": "http://localhost:9000/api/v1/itinerary/itineraries/1",
                            "body": {
                                "title": "Updated title",
                                "description": "Updated description"
                            }
                        }
                    },
                    {
                        "endpoint": "/api/v1/itineraries/{id}",
                        "method": "DELETE",
                        "description": "Xóa lịch trình",
                        "via_middleware": "/api/v1/itinerary/itineraries/1",
                        "example_request": {
                            "method": "DELETE",
                            "url": "http://localhost:9000/api/v1/itinerary/itineraries/1"
                        }
                    }
                ]
            }
        },
        "usage": {
            "routing_pattern": "http://localhost:9000/api/v1/{service}/{endpoint_path}",
            "note": "Tất cả requests đều đi qua middleware, không cần gọi trực tiếp tới backend services",
            "benefits": [
                "Single entry point",
                "Centralized authentication",
                "Request/response logging",
                "Load balancing",
                "Service discovery"
            ]
        }
    }


@router.get("/services/{service_name}", tags=["info"])
async def get_service_info(service_name: str):
    """
    Lấy thông tin chi tiết của một service cụ thể.
    """
    service_details = {
        "destination": {
            "name": "Destination Service",
            "description": "Quản lý thông tin điểm đến du lịch",
            "base_url": "http://localhost:8001",
            "health_check": "http://localhost:8001/health",
            "docs": "http://localhost:8001/docs",
            "technologies": ["FastAPI", "SQLAlchemy", "Alembic"],
            "database": "SQLite/PostgreSQL"
        },
        "weather": {
            "name": "Weather Service",
            "description": "Cung cấp thông tin thời tiết",
            "base_url": "http://localhost:8004",
            "health_check": "http://localhost:8004/health",
            "docs": "http://localhost:8004/docs",
            "technologies": ["FastAPI", "SQLAlchemy", "External Weather API"],
            "database": "SQLite/PostgreSQL"
        },
        "booking": {
            "name": "Booking Service",
            "description": "Tìm kiếm và đặt vé máy bay, khách sạn",
            "base_url": "http://localhost:8003",
            "health_check": "http://localhost:8003/health",
            "docs": "http://localhost:8003/api/docs",
            "technologies": ["FastAPI", "Redis", "Amadeus API"],
            "cache": "Redis",
            "external_apis": ["Amadeus Travel API"]
        },
        "itinerary": {
            "name": "Itinerary Service",
            "description": "Quản lý lịch trình du lịch",
            "base_url": "http://localhost:8002",
            "health_check": "http://localhost:8002/health",
            "technologies": ["FastAPI", "Pydantic"]
        }
    }
    
    if service_name not in service_details:
        return {
            "error": "Service not found",
            "available_services": list(service_details.keys())
        }
    
    return {
        "service": service_name,
        **service_details[service_name],
        "via_middleware": f"http://localhost:9000/api/v1/{service_name}"
    }
