from typing import Any

from fastapi import APIRouter, Body, Depends, Query, Request

from src.api.v1.dependencies import get_current_user
from .proxy import proxy_request


router = APIRouter()


@router.get("/destination/destinations", summary="Destination search")
async def destination_search(
    request: Request,
    query: str = Query(..., description="Search keyword"),
    country: str | None = Query(None, description="Country code filter"),
    user=Depends(get_current_user),
):
    return await proxy_request(service="destination", request=request, path="destinations")


@router.get("/destination/attractions", summary="Nearby attractions")
async def destination_attractions(
    request: Request,
    location: str = Query(..., description="Place name or address"),
    radius_m: int = Query(5000, description="Search radius in meters"),
    limit: int = Query(20, description="Max results"),
    user=Depends(get_current_user),
):
    return await proxy_request(service="destination", request=request, path="attractions")


@router.get("/destination/hotels", summary="Nearby hotels")
async def destination_hotels(
    request: Request,
    location: str = Query(..., description="Place name or address"),
    radius_m: int = Query(5000, description="Search radius in meters"),
    limit: int = Query(20, description="Max results"),
    user=Depends(get_current_user),
):
    return await proxy_request(service="destination", request=request, path="hotels")


@router.get("/weather/current", summary="Current weather")
async def weather_current(
    request: Request,
    location: str = Query(..., description="City or place name"),
    user=Depends(get_current_user),
):
    return await proxy_request(service="weather", request=request, path="weather/current")


@router.get("/weather/forecast", summary="Weather forecast")
async def weather_forecast(
    request: Request,
    location: str = Query(..., description="City or place name"),
    user=Depends(get_current_user),
):
    return await proxy_request(service="weather", request=request, path="forecast")


@router.post("/booking/flights/search", summary="Flight search")
async def booking_flight_search(
    request: Request,
    payload: dict[str, Any] = Body(..., description="Flight search payload"),
    user=Depends(get_current_user),
):
    return await proxy_request(
        service="booking", request=request, path="flights/search"
    )


@router.get("/booking/flights/{offer_id}", summary="Flight offer detail")
async def booking_flight_offer(
    request: Request,
    offer_id: str,
    user=Depends(get_current_user),
):
    return await proxy_request(
        service="booking", request=request, path=f"flights/{offer_id}"
    )


@router.get("/booking/flights/health", summary="Flights health")
async def booking_flights_health(request: Request, user=Depends(get_current_user)):
    return await proxy_request(service="booking", request=request, path="flights/health")


@router.post("/booking/hotels/search", summary="Hotel search")
async def booking_hotel_search(
    request: Request,
    payload: dict[str, Any] = Body(..., description="Hotel search payload"),
    user=Depends(get_current_user),
):
    return await proxy_request(
        service="booking", request=request, path="hotels/search"
    )


@router.post("/booking/hotels/offers", summary="Hotel offers")
async def booking_hotel_offers(
    request: Request,
    payload: dict[str, Any] = Body(..., description="Hotel offers payload"),
    user=Depends(get_current_user),
):
    return await proxy_request(
        service="booking", request=request, path="hotels/offers"
    )


@router.get("/booking/hotels/health", summary="Hotels health")
async def booking_hotels_health(request: Request, user=Depends(get_current_user)):
    return await proxy_request(service="booking", request=request, path="hotels/health")


@router.get("/booking/health", summary="Booking health")
async def booking_health(request: Request, user=Depends(get_current_user)):
    return await proxy_request(service="booking", request=request, path="health")


@router.get("/booking/cities", summary="Cities list")
async def booking_cities(
    request: Request,
    keyword: str | None = Query(None, description="City name or IATA code"),
    country_code: str | None = Query(None, description="Country code"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    user=Depends(get_current_user),
):
    return await proxy_request(service="booking", request=request, path="cities")


@router.get("/booking/cities/{iata_code}", summary="City detail")
async def booking_city_detail(
    request: Request,
    iata_code: str,
    user=Depends(get_current_user),
):
    return await proxy_request(
        service="booking", request=request, path=f"cities/{iata_code}"
    )


@router.post("/itinerary/itineraries", summary="Create itinerary")
async def itinerary_create(
    request: Request,
    payload: dict[str, Any] = Body(..., description="Itinerary payload"),
    user=Depends(get_current_user),
):
    return await proxy_request(
        service="itinerary", request=request, path="itineraries"
    )


@router.get("/itinerary/itineraries", summary="List itineraries")
async def itinerary_list(
    request: Request,
    user=Depends(get_current_user),
):
    return await proxy_request(
        service="itinerary", request=request, path="itineraries"
    )


@router.post("/itinerary/activities", summary="Add activity")
async def itinerary_activity(
    request: Request,
    payload: dict[str, Any] = Body(..., description="Activity payload"),
    user=Depends(get_current_user),
):
    return await proxy_request(
        service="itinerary", request=request, path="activities"
    )


@router.get("/itinerary/activities/{itinerary_id}", summary="List activities")
async def itinerary_activity_list(
    request: Request,
    itinerary_id: str,
    user=Depends(get_current_user),
):
    return await proxy_request(
        service="itinerary", request=request, path=f"activities/{itinerary_id}"
    )


@router.get("/itinerary/health", summary="Itinerary health")
async def itinerary_health(request: Request, user=Depends(get_current_user)):
    return await proxy_request(service="itinerary", request=request, path="health")
