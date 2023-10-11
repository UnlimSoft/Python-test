from typing import List

from fastapi import APIRouter, Query

from db import Session, City
from utils import exceptions, weather_api
from ..models.cities import CityMin, CityModel

router = APIRouter(prefix='/cities', tags=['Cities'])


@router.post(path='/create',
             summary='Create city',
             description='Создание города по его названию',
             response_model=CityModel)
def create(city: CityMin):
    if city is None:
        raise exceptions.ValueRequiredException('city')
    if not weather_api.check_city(city.name):
        raise exceptions.ValueInvalidException('city', 'Должен быть существующим городом')
    city_name = city.name.capitalize().strip()
    with Session() as s:
        city_object = s.query(City).filter(City.name == city_name).first()
        if city_object is None:
            city_object = City(name=city_name)
            s = Session()
            s.add(city_object)
            s.commit()

    return CityModel.from_orm(city_object)


@router.get('/get', description='List cities', response_model=List[CityModel])
def list_cities(q: List[str] = Query(description="Название города", default=None)):
    """
    Получение списка существующих городов. Если город отсутствует, то он будет проигнорирован
    """
    cities = Session().query(City).filter(City.name.in_(q))

    return [CityModel.from_orm(city) for city in cities]
