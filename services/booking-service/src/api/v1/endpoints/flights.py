from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
import logging

from schemas.flight import FlightSearchRequest, FlightSearchResponse, ErrorResponse
from core.use_cases.search_flights import SearchFlightsUseCase
from infrastructure.external.amadeus_client import AmadeusClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/flights", tags=["flights"])


def get_amadeus_client() -> AmadeusClient:
    return AmadeusClient()


def get_search_flights_use_case(
    amadeus_client: AmadeusClient = Depends(get_amadeus_client)
) -> SearchFlightsUseCase:
    return SearchFlightsUseCase(amadeus_client)


@router.post(
    "/search",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Tìm kiếm chuyến bay",
    description="Tìm kiếm chuyến bay giữa 2 địa điểm sử dụng Amadeus API",
    responses={
        200: {
            "description": "Tìm kiếm thành công",
            "content": {
                "application/json": {
                    "example": {
                        "meta": {"count": 10},
                        "data": [
                            {
                                "id": "1",
                                "source": "GDS",
                                "price": {
                                    "currency": "USD",
                                    "total": "250.00",
                                    "base": "200.00",
                                    "grand_total": "250.00"
                                }
                            }
                        ]
                    }
                }
            }
        },
        400: {"model": ErrorResponse, "description": "Yêu cầu không hợp lệ"},
        500: {"model": ErrorResponse, "description": "Lỗi server"}
    }
)
async def search_flights(
    search_request: FlightSearchRequest,
    use_case: SearchFlightsUseCase = Depends(get_search_flights_use_case)
) -> Dict[str, Any]:
    try:
        logger.info(f"Received flight search request: {search_request.origin} -> {search_request.destination}")
        
        result = await use_case.execute(search_request)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in search_flights endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tìm kiếm chuyến bay: {str(e)}"
        )


@router.get(
    "/{offer_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Lấy chi tiết chuyến bay",
    description="Lấy thông tin chi tiết của một chuyến bay theo offer ID",
    responses={
        200: {"description": "Lấy thông tin thành công"},
        404: {"model": ErrorResponse, "description": "Không tìm thấy chuyến bay"},
        500: {"model": ErrorResponse, "description": "Lỗi server"}
    }
)
async def get_flight_offer(
    offer_id: str,
    use_case: SearchFlightsUseCase = Depends(get_search_flights_use_case)
) -> Dict[str, Any]:
    try:
        logger.info(f"Received request for flight offer: {offer_id}")
        
        result = await use_case.get_flight_details(offer_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_flight_offer endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy thông tin chuyến bay: {str(e)}"
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Kiểm tra trạng thái",
    description="Endpoint để kiểm tra trạng thái hoạt động của flight service"
)
async def health_check() -> Dict[str, str]:
    return {
        "status": "healthy",
        "service": "flight-search",
        "version": "1.0.0"
    }
