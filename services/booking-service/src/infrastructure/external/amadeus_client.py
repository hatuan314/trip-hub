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
