from sqlalchemy import Column, String
from app.core.db import Base


class City(Base):
    __tablename__ = "cities"

    city = Column(String, primary_key=True, index=True)
    country_code = Column(String)
