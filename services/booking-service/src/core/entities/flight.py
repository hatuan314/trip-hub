from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Airport:
    iata_code: str
    terminal: Optional[str]
    timestamp: datetime


@dataclass
class Segment:
    departure: Airport
    arrival: Airport
    carrier_code: str
    flight_number: str
    aircraft_code: Optional[str]
    duration: str
    number_of_stops: int


@dataclass
class Price:
    currency: str
    total: float
    base: float
    grand_total: float
    fees: Optional[List[dict]] = None


@dataclass
class FlightEntity:
    id: str
    source: str
    one_way: bool
    segments: List[Segment]
    price: Price
    validating_airline_codes: List[str]
    number_of_bookable_seats: Optional[int] = None
    instant_ticketing_required: bool = False
    
    def get_total_duration(self) -> str:
        return self.segments[0].duration if self.segments else "PT0H0M"
    
    def get_departure_time(self) -> datetime:
        return self.segments[0].departure.timestamp if self.segments else datetime.now()
    
    def get_arrival_time(self) -> datetime:
        return self.segments[-1].arrival.timestamp if self.segments else datetime.now()
    
    def is_direct_flight(self) -> bool:
        return len(self.segments) == 1 and self.segments[0].number_of_stops == 0
    
    def get_total_stops(self) -> int:
        return sum(seg.number_of_stops for seg in self.segments) + (len(self.segments) - 1)
