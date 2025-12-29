from fastapi import APIRouter, HTTPException, Query

from src.config.settings import settings
from src.core.use_cases.get_nearby_hotels import GetNearbyHotels
from src.infrastructure.external.geoapify_client import GeoapifyClient
from src.schemas.hotel import HotelOut


router = APIRouter()


@router.get("/", summary="List hotels by location", response_model=list[HotelOut])
async def list_hotels(
    location: str = Query(..., description="Tên địa điểm hoặc địa chỉ cần tìm khách sạn gần đó"),
    radius_m: int = Query(5000, description="Bán kính tìm kiếm (m)"),
    limit: int = Query(20, description="Số kết quả tối đa"),
):
    # Geocode the input location, then query nearby accommodation places.
    if not settings.geoapify_api_key:
        raise HTTPException(status_code=500, detail="Missing GEOAPIFY_API_KEY")

    use_case = GetNearbyHotels(GeoapifyClient(api_key=settings.geoapify_api_key))
    hotels = await use_case.execute(location=location, radius_m=radius_m, limit=limit)
    return [HotelOut(**h.__dict__) for h in hotels]
