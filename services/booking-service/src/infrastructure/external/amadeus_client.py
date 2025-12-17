import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from config.settings import get_settings

logger = logging.getLogger(__name__)


class AmadeusClient:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.amadeus_base_url
        self.api_key = self.settings.amadeus_api_key
        self.api_secret = self.settings.amadeus_api_secret
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
    
    async def _get_access_token(self) -> str:
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                return self._access_token
        
        url = f"{self.base_url}/v1/security/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, data=data)
                response.raise_for_status()
                
                token_data = response.json()
                self._access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 1799)
                self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                
                logger.info("Successfully obtained Amadeus access token")
                return self._access_token
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to get Amadeus access token: {str(e)}")
            raise Exception(f"Authentication failed: {str(e)}")
    
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        adults: int = 1,
        return_date: Optional[str] = None,
        travel_class: Optional[str] = None,
        non_stop: bool = False,
        currency: str = "USD",
        max_results: int = 10
    ) -> Dict[str, Any]:
        token = await self._get_access_token()
        
        url = f"{self.base_url}/v2/shopping/flight-offers"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "originLocationCode": origin.upper(),
            "destinationLocationCode": destination.upper(),
            "departureDate": departure_date,
            "adults": adults,
            "currencyCode": currency,
            "max": max_results
        }
        
        if return_date:
            params["returnDate"] = return_date
        
        if travel_class:
            params["travelClass"] = travel_class.upper()
        
        if non_stop:
            params["nonStop"] = "true"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Successfully searched flights from {origin} to {destination}")
                return data
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to search flights: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"Flight search failed: {str(e)}")
    
    async def get_flight_offer(self, offer_id: str) -> Dict[str, Any]:
        token = await self._get_access_token()
        
        url = f"{self.base_url}/v2/shopping/flight-offers/{offer_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Successfully retrieved flight offer: {offer_id}")
                return data
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to get flight offer: {str(e)}")
            raise Exception(f"Failed to retrieve flight offer: {str(e)}")
    
    async def get_hotels_by_city(
        self,
        city_code: str,
        radius: int = 5,
        radius_unit: str = "KM"
    ) -> Dict[str, Any]:
        token = await self._get_access_token()
        
        url = f"{self.base_url}/v1/reference-data/locations/hotels/by-city"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "cityCode": city_code.upper(),
            "radius": radius,
            "radiusUnit": radius_unit
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Found {len(data.get('data', []))} hotels in {city_code}")
                return data
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to get hotels by city: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"Failed to get hotels by city: {str(e)}")
    
    async def search_hotels(
        self,
        city_code: str,
        check_in_date: str,
        check_out_date: str,
        adults: int = 1,
        children: int = 0,
        rooms: int = 1,
        radius: int = 5,
        radius_unit: str = "KM",
        currency: str = "USD",
        payment_policy: Optional[str] = None,
        board_type: Optional[str] = None,
        max_results: int = 10
    ) -> Dict[str, Any]:
        try:
            hotels_data = await self.get_hotels_by_city(city_code, radius, radius_unit)
            
            if not hotels_data.get('data'):
                logger.warning(f"No hotels found in {city_code}")
                return {"data": [], "meta": {"count": 0}}
            
            hotel_ids = [hotel['hotelId'] for hotel in hotels_data['data'][:max_results]]
            
            if not hotel_ids:
                return {"data": [], "meta": {"count": 0}}
            
            token = await self._get_access_token()
            
            url = f"{self.base_url}/v3/shopping/hotel-offers"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "hotelIds": ",".join(hotel_ids),
                "checkInDate": check_in_date,
                "checkOutDate": check_out_date,
                "adults": adults,
                "roomQuantity": rooms,
                "currency": currency,
                "bestRateOnly": "true"
            }
            
            if payment_policy:
                params["paymentPolicy"] = payment_policy
            
            if board_type:
                params["boardType"] = board_type
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if "data" in data and len(data["data"]) > max_results:
                    data["data"] = data["data"][:max_results]
                
                logger.info(f"Successfully searched hotels in {city_code}, found {len(data.get('data', []))} offers")
                return data
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to search hotels: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"Hotel search failed: {str(e)}")
    
    async def get_hotel_offers(
        self,
        hotel_id: str,
        check_in_date: str,
        check_out_date: str,
        adults: int = 1,
        rooms: int = 1,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        token = await self._get_access_token()
        
        url = f"{self.base_url}/v3/shopping/hotel-offers"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "hotelIds": hotel_id,
            "checkInDate": check_in_date,
            "checkOutDate": check_out_date,
            "adults": adults,
            "roomQuantity": rooms,
            "currency": currency
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Successfully retrieved hotel offers for: {hotel_id}")
                return data
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to get hotel offers: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"Failed to retrieve hotel offers: {str(e)}")
