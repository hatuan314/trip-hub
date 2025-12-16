import logging
from typing import Dict, Any
from infrastructure.external.amadeus_client import AmadeusClient
from schemas.flight import FlightSearchRequest

logger = logging.getLogger(__name__)


class SearchFlightsUseCase:
    def __init__(self, amadeus_client: AmadeusClient):
        self.amadeus_client = amadeus_client
    
    async def execute(self, search_request: FlightSearchRequest) -> Dict[str, Any]:
        logger.info(f"Searching flights from {search_request.origin} to {search_request.destination}")
        
        try:
            result = await self.amadeus_client.search_flights(
                origin=search_request.origin,
                destination=search_request.destination,
                departure_date=search_request.departure_date,
                adults=search_request.adults,
                return_date=search_request.return_date,
                travel_class=search_request.travel_class,
                non_stop=search_request.non_stop,
                currency=search_request.currency,
                max_results=search_request.max_results
            )
            
            logger.info(f"Found {len(result.get('data', []))} flight offers")
            return result
            
        except Exception as e:
            logger.error(f"Error searching flights: {str(e)}")
            raise
    
    async def get_flight_details(self, offer_id: str) -> Dict[str, Any]:
        logger.info(f"Getting flight details for offer: {offer_id}")
        
        try:
            result = await self.amadeus_client.get_flight_offer(offer_id)
            logger.info(f"Successfully retrieved flight offer details")
            return result
            
        except Exception as e:
            logger.error(f"Error getting flight details: {str(e)}")
            raise
