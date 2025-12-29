from fastapi import APIRouter, HTTPException, Query

from src.config.settings import settings
from src.core.use_cases.get_destination_info import GetDestinationInfo
from src.core.use_cases.search_destinations import SearchDestinations
from src.infrastructure.external.geoapify_client import GeoapifyClient
from src.schemas.destination import DestinationOut


router = APIRouter()


@router.get("/", summary="Search destinations", response_model=list[DestinationOut])
async def list_destinations(query: str = Query(..., description="Từ khóa địa điểm"), country: str | None = None):
    # Require API key before calling external Geoapify APIs.
    if not settings.geoapify_api_key:
        raise HTTPException(status_code=500, detail="Missing GEOAPIFY_API_KEY")
    client = GeoapifyClient(api_key=settings.geoapify_api_key)
    use_case = SearchDestinations([client])
    results = await use_case.execute(query=query, country=country)
    return [DestinationOut(**d.__dict__) for d in results]


@router.get("/{destination_query}", summary="Get destination detail", response_model=DestinationOut | None)
async def get_destination(destination_query: str):
    # Resolve a single destination by taking the first match from Geoapify.
    if not settings.geoapify_api_key:
        raise HTTPException(status_code=500, detail="Missing GEOAPIFY_API_KEY")
    client = GeoapifyClient(api_key=settings.geoapify_api_key)
    use_case = GetDestinationInfo(client)
    result = await use_case.execute(destination_query)
    if not result:
        raise HTTPException(status_code=404, detail="Destination not found")
    return DestinationOut(**result.__dict__)
