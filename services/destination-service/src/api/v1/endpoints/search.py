from fastapi import APIRouter, HTTPException

from src.config.settings import settings
from src.core.use_cases.search_destinations import SearchDestinations
from src.infrastructure.external.geoapify_client import GeoapifyClient
from src.schemas.destination import DestinationOut


router = APIRouter()


@router.get("/", summary="Search destinations", response_model=list[DestinationOut])
async def search_destinations(query: str, country: str | None = None):
    clients = []
    if settings.geoapify_api_key:
        clients.append(GeoapifyClient(api_key=settings.geoapify_api_key))

    if not clients:
        raise HTTPException(status_code=500, detail="Missing external API keys")

    use_case = SearchDestinations(clients)
    destinations = await use_case.execute(query=query, country=country)
    return [DestinationOut(**dest.__dict__) for dest in destinations]
