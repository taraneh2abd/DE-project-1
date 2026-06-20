from pydantic import BaseModel


class CitySchema(BaseModel):
    city: str
    country_code: str
