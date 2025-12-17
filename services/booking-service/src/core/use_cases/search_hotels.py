import logging
from typing import Dict, Any
from infrastructure.external.amadeus_client import AmadeusClient
from schemas.hotel import HotelSearchRequest, HotelDetailsRequest

logger = logging.getLogger(__name__)


class SearchHotelsUseCase:
    def __init__(self, amadeus_client: AmadeusClient):
        self.amadeus_client = amadeus_client
    
    async def execute(self, search_request: HotelSearchRequest) -> Dict[str, Any]:
        logger.info(f"Searching hotels in {search_request.city_code}")
        
        try:
            result = await self.amadeus_client.search_hotels(
                city_code=search_request.city_code,
                check_in_date=search_request.check_in_date,
                check_out_date=search_request.check_out_date,
                adults=search_request.adults,
                children=search_request.children or 0,
                rooms=search_request.rooms or 1,
                radius=search_request.radius or 5,
                radius_unit=search_request.radius_unit or "KM",
                currency=search_request.currency or "USD",
                payment_policy=search_request.payment_policy,
                board_type=search_request.board_type,
                max_results=search_request.max_results or 10
            )
            
            hotel_count = len(result.get('data', []))
            logger.info(f"Found {hotel_count} hotels in {search_request.city_code}")
            return result
            
        except Exception as e:
            logger.error(f"Error searching hotels: {str(e)}")
            raise
    
    async def get_hotel_details(self, details_request: HotelDetailsRequest) -> Dict[str, Any]:
        logger.info(f"Getting hotel details for: {details_request.hotel_id}")
        
        try:
            result = await self.amadeus_client.get_hotel_offers(
                hotel_id=details_request.hotel_id,
                check_in_date=details_request.check_in_date,
                check_out_date=details_request.check_out_date,
                adults=details_request.adults,
                rooms=details_request.rooms or 1,
                currency=details_request.currency or "USD"
            )
            
            logger.info(f"Successfully retrieved hotel details")
            return result
            
        except Exception as e:
            logger.error(f"Error getting hotel details: {str(e)}")
            raise
