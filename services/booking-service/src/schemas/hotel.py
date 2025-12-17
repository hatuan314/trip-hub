from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class HotelSearchRequest(BaseModel):
    city_code: str = Field(..., description="Mã IATA của thành phố (VD: BKK, SIN, NYC)", min_length=3, max_length=3)
    check_in_date: str = Field(..., description="Ngày nhận phòng (YYYY-MM-DD)", pattern=r"^\d{4}-\d{2}-\d{2}$")
    check_out_date: str = Field(..., description="Ngày trả phòng (YYYY-MM-DD)", pattern=r"^\d{4}-\d{2}-\d{2}$")
    adults: int = Field(..., description="Số người lớn", ge=1, le=9)
    children: Optional[int] = Field(0, description="Số trẻ em", ge=0, le=9)
    rooms: Optional[int] = Field(1, description="Số phòng", ge=1, le=9)
    radius: Optional[int] = Field(5, description="Bán kính tìm kiếm (km)", ge=1, le=300)
    radius_unit: Optional[str] = Field("KM", description="Đơn vị bán kính: KM hoặc MILE")
    currency: Optional[str] = Field("USD", description="Đơn vị tiền tệ", max_length=3)
    payment_policy: Optional[str] = Field(None, description="GUARANTEE, DEPOSIT, NONE")
    board_type: Optional[str] = Field(None, description="ROOM_ONLY, BREAKFAST, HALF_BOARD, FULL_BOARD, ALL_INCLUSIVE")
    max_results: Optional[int] = Field(10, description="Số lượng kết quả tối đa", ge=1, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "city_code": "BKK",
                "check_in_date": "2025-02-01",
                "check_out_date": "2025-02-05",
                "adults": 2,
                "children": 1,
                "rooms": 1,
                "radius": 10,
                "currency": "USD",
                "max_results": 10
            }
        }


class HotelAddress(BaseModel):
    lines: Optional[List[str]] = None
    postal_code: Optional[str] = None
    city_name: Optional[str] = None
    country_code: Optional[str] = None


class HotelContact(BaseModel):
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None


class HotelGeoCode(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class HotelMedia(BaseModel):
    uri: Optional[str] = None
    category: Optional[str] = None


class HotelAmenity(BaseModel):
    description: Optional[str] = None
    amenity_type: Optional[str] = None
    amenity_provider: Optional[str] = None


class RoomTypeEstimated(BaseModel):
    category: Optional[str] = None
    beds: Optional[int] = None
    bed_type: Optional[str] = None


class RoomDescription(BaseModel):
    text: Optional[str] = None
    lang: Optional[str] = None


class RoomOffer(BaseModel):
    id: Optional[str] = None
    room_type: Optional[str] = None
    description: Optional[RoomDescription] = None
    guests: Optional[dict] = None
    price: Optional[dict] = None
    policies: Optional[dict] = None
    self_link: Optional[str] = None


class HotelOffer(BaseModel):
    hotel_id: str
    chain_code: Optional[str] = None
    name: Optional[str] = None
    rating: Optional[str] = None
    cityCode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[HotelAddress] = None
    contact: Optional[HotelContact] = None
    description: Optional[dict] = None
    amenities: Optional[List[str]] = None
    media: Optional[List[HotelMedia]] = None
    available: Optional[bool] = None
    offers: Optional[List[RoomOffer]] = None
    self_link: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "hotel_id": "BKXXX001",
                "name": "Grand Hotel Bangkok",
                "rating": "5",
                "cityCode": "BKK",
                "latitude": 13.7563,
                "longitude": 100.5018,
                "available": True
            }
        }


class HotelSearchResponse(BaseModel):
    data: List[HotelOffer]
    meta: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "hotel_id": "BKXXX001",
                        "name": "Grand Hotel Bangkok",
                        "rating": "5",
                        "cityCode": "BKK",
                        "available": True
                    }
                ],
                "meta": {
                    "count": 10
                }
            }
        }


class HotelDetailsRequest(BaseModel):
    hotel_id: str = Field(..., description="ID của khách sạn")
    check_in_date: str = Field(..., description="Ngày nhận phòng (YYYY-MM-DD)", pattern=r"^\d{4}-\d{2}-\d{2}$")
    check_out_date: str = Field(..., description="Ngày trả phòng (YYYY-MM-DD)", pattern=r"^\d{4}-\d{2}-\d{2}$")
    adults: int = Field(..., description="Số người lớn", ge=1, le=9)
    rooms: Optional[int] = Field(1, description="Số phòng", ge=1, le=9)
    currency: Optional[str] = Field("USD", description="Đơn vị tiền tệ", max_length=3)


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Hotel search failed",
                "detail": "Invalid city code",
                "status_code": 400
            }
        }
