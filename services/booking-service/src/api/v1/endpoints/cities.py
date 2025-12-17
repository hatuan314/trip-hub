from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
import logging

from schemas.city import City, CitiesResponse, CitySearchRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cities", tags=["cities"])

CITIES_DATA = [
    {"iata_code": "HAN", "name": "Hanoi", "country": "Vietnam", "country_code": "VN"},
    {"iata_code": "SGN", "name": "Ho Chi Minh City", "country": "Vietnam", "country_code": "VN"},
    {"iata_code": "DAD", "name": "Da Nang", "country": "Vietnam", "country_code": "VN"},
    {"iata_code": "BKK", "name": "Bangkok", "country": "Thailand", "country_code": "TH"},
    {"iata_code": "SIN", "name": "Singapore", "country": "Singapore", "country_code": "SG"},
    {"iata_code": "KUL", "name": "Kuala Lumpur", "country": "Malaysia", "country_code": "MY"},
    {"iata_code": "MNL", "name": "Manila", "country": "Philippines", "country_code": "PH"},
    {"iata_code": "JKT", "name": "Jakarta", "country": "Indonesia", "country_code": "ID"},
    {"iata_code": "HKG", "name": "Hong Kong", "country": "Hong Kong", "country_code": "HK"},
    {"iata_code": "TPE", "name": "Taipei", "country": "Taiwan", "country_code": "TW"},
    {"iata_code": "TYO", "name": "Tokyo", "country": "Japan", "country_code": "JP"},
    {"iata_code": "OSA", "name": "Osaka", "country": "Japan", "country_code": "JP"},
    {"iata_code": "SEL", "name": "Seoul", "country": "South Korea", "country_code": "KR"},
    {"iata_code": "PEK", "name": "Beijing", "country": "China", "country_code": "CN"},
    {"iata_code": "SHA", "name": "Shanghai", "country": "China", "country_code": "CN"},
    {"iata_code": "BOM", "name": "Mumbai", "country": "India", "country_code": "IN"},
    {"iata_code": "DEL", "name": "Delhi", "country": "India", "country_code": "IN"},
    {"iata_code": "DXB", "name": "Dubai", "country": "United Arab Emirates", "country_code": "AE"},
    {"iata_code": "DOH", "name": "Doha", "country": "Qatar", "country_code": "QA"},
    {"iata_code": "IST", "name": "Istanbul", "country": "Turkey", "country_code": "TR"},
    {"iata_code": "LON", "name": "London", "country": "United Kingdom", "country_code": "GB"},
    {"iata_code": "PAR", "name": "Paris", "country": "France", "country_code": "FR"},
    {"iata_code": "ROM", "name": "Rome", "country": "Italy", "country_code": "IT"},
    {"iata_code": "BCN", "name": "Barcelona", "country": "Spain", "country_code": "ES"},
    {"iata_code": "MAD", "name": "Madrid", "country": "Spain", "country_code": "ES"},
    {"iata_code": "BER", "name": "Berlin", "country": "Germany", "country_code": "DE"},
    {"iata_code": "MUC", "name": "Munich", "country": "Germany", "country_code": "DE"},
    {"iata_code": "AMS", "name": "Amsterdam", "country": "Netherlands", "country_code": "NL"},
    {"iata_code": "VIE", "name": "Vienna", "country": "Austria", "country_code": "AT"},
    {"iata_code": "PRG", "name": "Prague", "country": "Czech Republic", "country_code": "CZ"},
    {"iata_code": "NYC", "name": "New York", "country": "United States", "country_code": "US"},
    {"iata_code": "LAX", "name": "Los Angeles", "country": "United States", "country_code": "US"},
    {"iata_code": "SFO", "name": "San Francisco", "country": "United States", "country_code": "US"},
    {"iata_code": "CHI", "name": "Chicago", "country": "United States", "country_code": "US"},
    {"iata_code": "MIA", "name": "Miami", "country": "United States", "country_code": "US"},
    {"iata_code": "YTO", "name": "Toronto", "country": "Canada", "country_code": "CA"},
    {"iata_code": "YVR", "name": "Vancouver", "country": "Canada", "country_code": "CA"},
    {"iata_code": "MEX", "name": "Mexico City", "country": "Mexico", "country_code": "MX"},
    {"iata_code": "SAO", "name": "Sao Paulo", "country": "Brazil", "country_code": "BR"},
    {"iata_code": "RIO", "name": "Rio de Janeiro", "country": "Brazil", "country_code": "BR"},
    {"iata_code": "BUE", "name": "Buenos Aires", "country": "Argentina", "country_code": "AR"},
    {"iata_code": "SYD", "name": "Sydney", "country": "Australia", "country_code": "AU"},
    {"iata_code": "MEL", "name": "Melbourne", "country": "Australia", "country_code": "AU"},
    {"iata_code": "AKL", "name": "Auckland", "country": "New Zealand", "country_code": "NZ"},
    {"iata_code": "CPT", "name": "Cape Town", "country": "South Africa", "country_code": "ZA"},
    {"iata_code": "JNB", "name": "Johannesburg", "country": "South Africa", "country_code": "ZA"},
    {"iata_code": "CAI", "name": "Cairo", "country": "Egypt", "country_code": "EG"},
]


@router.get(
    "",
    response_model=CitiesResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách thành phố",
    description="Lấy danh sách tất cả các thành phố với mã IATA và tên đầy đủ. Hỗ trợ tìm kiếm và lọc.",
    responses={
        200: {
            "description": "Lấy danh sách thành công",
            "content": {
                "application/json": {
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
                            "count": 2,
                            "total": 47
                        }
                    }
                }
            }
        }
    }
)
async def get_cities(
    keyword: Optional[str] = Query(None, description="Tìm kiếm theo tên thành phố hoặc mã IATA"),
    country_code: Optional[str] = Query(None, description="Lọc theo mã quốc gia (VD: VN, TH, US)", min_length=2, max_length=2),
    limit: int = Query(50, description="Số lượng kết quả tối đa", ge=1, le=100)
) -> CitiesResponse:
    try:
        logger.info(f"Fetching cities list with keyword={keyword}, country_code={country_code}, limit={limit}")
        
        filtered_cities = CITIES_DATA.copy()
        
        if country_code:
            country_code_upper = country_code.upper()
            filtered_cities = [
                city for city in filtered_cities 
                if city["country_code"] == country_code_upper
            ]
            logger.info(f"Filtered by country_code={country_code_upper}: {len(filtered_cities)} cities")
        
        if keyword:
            keyword_lower = keyword.lower()
            filtered_cities = [
                city for city in filtered_cities
                if keyword_lower in city["name"].lower() or keyword_lower in city["iata_code"].lower()
            ]
            logger.info(f"Filtered by keyword={keyword}: {len(filtered_cities)} cities")
        
        total_count = len(filtered_cities)
        
        filtered_cities = filtered_cities[:limit]
        
        cities = [City(**city) for city in filtered_cities]
        
        return CitiesResponse(
            data=cities,
            meta={
                "count": len(cities),
                "total": total_count,
                "limit": limit
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching cities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách thành phố: {str(e)}"
        )


@router.get(
    "/{iata_code}",
    response_model=City,
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin thành phố theo mã IATA",
    description="Lấy thông tin chi tiết của một thành phố dựa trên mã IATA",
    responses={
        200: {"description": "Lấy thông tin thành công"},
        404: {"description": "Không tìm thấy thành phố"}
    }
)
async def get_city_by_code(iata_code: str) -> City:
    try:
        logger.info(f"Fetching city with IATA code: {iata_code}")
        
        iata_code_upper = iata_code.upper()
        
        city_data = next(
            (city for city in CITIES_DATA if city["iata_code"] == iata_code_upper),
            None
        )
        
        if not city_data:
            logger.warning(f"City not found: {iata_code_upper}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy thành phố với mã IATA: {iata_code_upper}"
            )
        
        return City(**city_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching city: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy thông tin thành phố: {str(e)}"
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Kiểm tra trạng thái",
    description="Endpoint để kiểm tra trạng thái hoạt động của cities service"
)
async def health_check():
    return {
        "status": "healthy",
        "service": "cities",
        "version": "1.0.0",
        "total_cities": len(CITIES_DATA)
    }
