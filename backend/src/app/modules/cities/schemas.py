from pydantic import BaseModel


class CityOut(BaseModel):
    id: int
    slug: str
    name: str
    lat: float
    lng: float
