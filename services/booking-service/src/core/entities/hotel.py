from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class HotelAddress:
    lines: Optional[List[str]]
    postal_code: Optional[str]
    city_name: Optional[str]
    country_code: Optional[str]


@dataclass
class HotelLocation:
    latitude: float
    longitude: float


@dataclass
class HotelAmenity:
    name: str
    category: Optional[str] = None


@dataclass
class RoomPrice:
    currency: str
    total: float
    base: float
    taxes: Optional[float] = None
    fees: Optional[float] = None


@dataclass
class Room:
    room_id: str
    room_type: str
    description: Optional[str]
    capacity: int
    price: RoomPrice
    available: bool


@dataclass
class HotelEntity:
    hotel_id: str
    name: str
    city_code: str
    rating: Optional[str]
    location: Optional[HotelLocation]
    address: Optional[HotelAddress]
    amenities: List[HotelAmenity]
    rooms: List[Room]
    available: bool
    
    def get_min_price(self) -> Optional[float]:
        if not self.rooms:
            return None
        available_rooms = [r for r in self.rooms if r.available]
        if not available_rooms:
            return None
        return min(room.price.total for room in available_rooms)
    
    def get_max_price(self) -> Optional[float]:
        if not self.rooms:
            return None
        available_rooms = [r for r in self.rooms if r.available]
        if not available_rooms:
            return None
        return max(room.price.total for room in available_rooms)
    
    def has_amenity(self, amenity_name: str) -> bool:
        return any(a.name.lower() == amenity_name.lower() for a in self.amenities)
    
    def get_available_rooms(self) -> List[Room]:
        return [room for room in self.rooms if room.available]
    
    def get_distance_from(self, lat: float, lon: float) -> Optional[float]:
        if not self.location:
            return None
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371
        
        lat1 = radians(self.location.latitude)
        lon1 = radians(self.location.longitude)
        lat2 = radians(lat)
        lon2 = radians(lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
