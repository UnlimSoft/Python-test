from pydantic import BaseModel, Field


class CityMin(BaseModel):
    name: str = Field(description='Название города')


class BaseCity(CityMin):
    weather: float = Field(description='Текущая температура в городе')


class CityModel(BaseCity):
    id: int

    class Config:
        orm_mode = True
