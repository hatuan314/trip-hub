from fastapi import APIRouter, HTTPException, Query

from src.config.settings import settings
from src.core.use_cases.get_attractions import GetAttractions
from src.infrastructure.external.geoapify_client import GeoapifyClient
from src.schemas.attraction import AttractionOut


router = APIRouter()


@router.get("/", summary="List attractions by location", response_model=list[AttractionOut])
async def list_attractions(
    location: str = Query(..., description="Tên địa điểm hoặc địa chỉ cần tìm điểm tham quan gần đó"),
    radius_m: int = Query(5000, description="Bán kính tìm kiếm (m)"),
    limit: int = Query(20, description="Số kết quả tối đa"),
):
    if not settings.geoapify_api_key:
        raise HTTPException(status_code=500, detail="Missing GEOAPIFY_API_KEY")

    use_case = GetAttractions(GeoapifyClient(api_key=settings.geoapify_api_key))
    attractions = await use_case.execute(location=location, radius_m=radius_m, limit=limit)
    return [AttractionOut(**a.__dict__) for a in attractions]
