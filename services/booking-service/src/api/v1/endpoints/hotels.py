from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
import logging

from schemas.hotel import HotelSearchRequest, HotelDetailsRequest, HotelSearchResponse, ErrorResponse
from core.use_cases.search_hotels import SearchHotelsUseCase
from infrastructure.external.amadeus_client import AmadeusClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hotels", tags=["hotels"])


def get_amadeus_client() -> AmadeusClient:
    return AmadeusClient()


def get_search_hotels_use_case(
    amadeus_client: AmadeusClient = Depends(get_amadeus_client)
) -> SearchHotelsUseCase:
    return SearchHotelsUseCase(amadeus_client)


@router.post(
    "/search",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Tìm kiếm khách sạn",
    description="Tìm kiếm khách sạn theo thành phố sử dụng Amadeus API",
    responses={
        200: {
            "description": "Tìm kiếm thành công",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "type": "hotel-offers",
                                "hotel": {
                                    "hotelId": "BKXXX001",
                                    "name": "Grand Hotel Bangkok",
                                    "rating": "5",
                                    "cityCode": "BKK"
                                },
                                "available": True,
                                "offers": [
                                    {
                                        "id": "OFFER123",
                                        "price": {
                                            "currency": "USD",
                                            "total": "150.00"
                                        }
                                    }
                                ]
                            }
                        ],
                        "meta": {
                            "count": 10
                        }
                    }
                }
            }
        },
        400: {"model": ErrorResponse, "description": "Yêu cầu không hợp lệ"},
        500: {"model": ErrorResponse, "description": "Lỗi server"}
    }
)
async def search_hotels(
    search_request: HotelSearchRequest,
    use_case: SearchHotelsUseCase = Depends(get_search_hotels_use_case)
) -> Dict[str, Any]:
    try:
        logger.info(f"Received hotel search request for city: {search_request.city_code}")
        
        result = await use_case.execute(search_request)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in search_hotels endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tìm kiếm khách sạn: {str(e)}"
        )


@router.post(
    "/offers",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Lấy chi tiết khách sạn và giá phòng",
    description="Lấy thông tin chi tiết về khách sạn và các phòng có sẵn",
    responses={
        200: {"description": "Lấy thông tin thành công"},
        404: {"model": ErrorResponse, "description": "Không tìm thấy khách sạn"},
        500: {"model": ErrorResponse, "description": "Lỗi server"}
    }
)
async def get_hotel_offers(
    details_request: HotelDetailsRequest,
    use_case: SearchHotelsUseCase = Depends(get_search_hotels_use_case)
) -> Dict[str, Any]:
    try:
        logger.info(f"Received request for hotel offers: {details_request.hotel_id}")
        
        result = await use_case.get_hotel_details(details_request)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_hotel_offers endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy thông tin khách sạn: {str(e)}"
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Kiểm tra trạng thái",
    description="Endpoint để kiểm tra trạng thái hoạt động của hotel service"
)
async def health_check() -> Dict[str, str]:
    return {
        "status": "healthy",
        "service": "hotel-search",
        "version": "1.0.0"
    }
