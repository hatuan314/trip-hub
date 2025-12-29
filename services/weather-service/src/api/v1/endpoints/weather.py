from fastapi import APIRouter, HTTPException, Query
import httpx

from src.config.settings import settings
from src.core.use_cases.get_current_weather import GetCurrentWeather
from src.infrastructure.external.openweather_client import OpenWeatherClient
from src.schemas.weather import WeatherOut


router = APIRouter()


@router.get("/current", summary="Current weather", response_model=WeatherOut)
async def current_weather(location: str = Query(..., description="City or place name")):
    # Kiểm tra API key trước khi gọi OpenWeather.
    if not settings.openweather_api_key:
        raise HTTPException(status_code=500, detail="Missing OPENWEATHER_API_KEY")

    client = OpenWeatherClient(api_key=settings.openweather_api_key)
    use_case = GetCurrentWeather(client)
    try:
        # Use case chỉ ủy quyền cho client gọi API và map dữ liệu.
        weather = await use_case.execute(location)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status == 401:
            raise HTTPException(status_code=401, detail="OpenWeather unauthorized, check API key") from exc
        raise HTTPException(status_code=502, detail=f"OpenWeather error: {status}") from exc
    return WeatherOut(**weather.__dict__)
