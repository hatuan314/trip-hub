from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FlightSearchRequest(BaseModel):
    origin: str = Field(..., description="IATA code của sân bay xuất phát (VD: HAN, SGN)", min_length=3, max_length=3)
    destination: str = Field(..., description="IATA code của sân bay đến (VD: BKK, SIN)", min_length=3, max_length=3)
    departure_date: str = Field(..., description="Ngày khởi hành (YYYY-MM-DD)", pattern=r"^\d{4}-\d{2}-\d{2}$")
    return_date: Optional[str] = Field(None, description="Ngày về (YYYY-MM-DD) - để trống nếu 1 chiều", pattern=r"^\d{4}-\d{2}-\d{2}$")
    adults: int = Field(1, description="Số lượng hành khách người lớn", ge=1, le=9)
    travel_class: Optional[str] = Field(None, description="Hạng vé: ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST")
    non_stop: bool = Field(False, description="Chỉ tìm chuyến bay thẳng")
    currency: str = Field("USD", description="Đơn vị tiền tệ", max_length=3)
    max_results: int = Field(10, description="Số lượng kết quả tối đa", ge=1, le=250)
    
    class Config:
        json_schema_extra = {
            "example": {
                "origin": "HAN",
                "destination": "BKK",
                "departure_date": "2024-12-25",
                "return_date": "2024-12-30",
                "adults": 2,
                "travel_class": "ECONOMY",
                "non_stop": False,
                "currency": "USD",
                "max_results": 10
            }
        }


class AirportInfo(BaseModel):
    iata_code: str
    terminal: Optional[str] = None
    at: datetime


class FlightSegment(BaseModel):
    departure: AirportInfo
    arrival: AirportInfo
    carrier_code: str
    flight_number: str
    aircraft_code: Optional[str] = None
    duration: str
    number_of_stops: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "departure": {
                    "iata_code": "HAN",
                    "terminal": "1",
                    "at": "2024-12-25T10:00:00"
                },
                "arrival": {
                    "iata_code": "BKK",
                    "terminal": "2",
                    "at": "2024-12-25T12:30:00"
                },
                "carrier_code": "VN",
                "flight_number": "607",
                "aircraft_code": "321",
                "duration": "PT2H30M",
                "number_of_stops": 0
            }
        }


class PriceDetail(BaseModel):
    currency: str
    total: str
    base: str
    fees: Optional[List[dict]] = None
    grand_total: str


class FlightOffer(BaseModel):
    id: str
    source: str
    instant_ticketing_required: bool
    non_homogeneous: bool
    one_way: bool
    last_ticketing_date: Optional[str] = None
    number_of_bookable_seats: Optional[int] = None
    itineraries: List[dict]
    price: PriceDetail
    pricing_options: dict
    validating_airline_codes: List[str]
    traveler_pricings: List[dict]


class FlightSearchResponse(BaseModel):
    meta: dict
    data: List[FlightOffer]
    dictionaries: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "meta": {
                    "count": 10,
                    "links": {
                        "self": "https://test.api.amadeus.com/v2/shopping/flight-offers?..."
                    }
                },
                "data": [
                    {
                        "id": "1",
                        "source": "GDS",
                        "instant_ticketing_required": False,
                        "non_homogeneous": False,
                        "one_way": False,
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


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Flight search failed",
                "detail": "Invalid IATA code",
                "status_code": 400
            }
        }
