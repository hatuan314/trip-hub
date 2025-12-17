from pydantic import BaseModel, Field
from typing import List, Optional


class City(BaseModel):
    iata_code: str = Field(..., description="Mã IATA của thành phố (3 ký tự)")
    name: str = Field(..., description="Tên đầy đủ của thành phố")
    country: str = Field(..., description="Tên quốc gia")
    country_code: Optional[str] = Field(None, description="Mã quốc gia (2 ký tự)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "iata_code": "BKK",
                "name": "Bangkok",
                "country": "Thailand",
                "country_code": "TH"
            }
        }


class CitiesResponse(BaseModel):
    data: List[City]
    meta: dict = Field(default_factory=lambda: {"count": 0})
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "iata_code": "BKK",
                        "name": "Bangkok",
                        "country": "Thailand",
                        "country_code": "TH"
                    },
                    {
                        "iata_code": "SIN",
                        "name": "Singapore",
                        "country": "Singapore",
                        "country_code": "SG"
                    }
                ],
                "meta": {
                    "count": 2
                }
            }
        }


class CitySearchRequest(BaseModel):
    keyword: Optional[str] = Field(None, description="Từ khóa tìm kiếm (tên thành phố hoặc mã IATA)")
    country_code: Optional[str] = Field(None, description="Lọc theo mã quốc gia", min_length=2, max_length=2)
    limit: Optional[int] = Field(50, description="Số lượng kết quả tối đa", ge=1, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "keyword": "Bangkok",
                "limit": 10
            }
        }
