import datetime as dt
from typing import List, Optional, Literal

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import func

from database import Session, City, User, Picnic, PicnicRegistration
from external_requests import CheckCityExisting
from models import RegisterUserRequest, UserModel

app = FastAPI()


@app.get('/create-city/', summary='Create City', description='Создание города по его названию')
def create_city(city: str = Query(description="Название города", default=None)):
    if city is None:
        raise HTTPException(status_code=400, detail='Параметр city должен быть указан')
    check = CheckCityExisting()
    if not check.check_existing(city):
        raise HTTPException(status_code=400, detail='Параметр city должен быть существующим городом')

    city_object = Session().query(City).filter(City.name == city.capitalize()).first()
    if city_object is None:
        city_object = City(name=city.capitalize())
        s = Session()
        s.add(city_object)
        s.commit()

    return {'id': city_object.id, 'name': city_object.name, 'weather': city_object.weather}


@app.post('/get-cities/', summary='Get Cities')
def cities_list(q: List[str] = Query(description="Название города", default=None)):
    """
    Получение списка существующих городов. Если город отсутствует, то он будет проигнорирован
    """
    cities = Session().query(City).filter(City.name.in_(q))

    return [{'id': city.id, 'name': city.name, 'weather': city.weather} for city in cities]


@app.post('/users-list/', summary='')
def users_list(filter_age: Optional[Literal["min", "max"]] = Query(description="Фильтрация пользователей по возрасту",
                                                                   default=None)):
    """
    Список пользователей
    """
    if not filter_age:
        users = Session().query(User).all()
    else:
        s = Session()
        subquery = s.query(getattr(func, filter_age)(User.age)).scalar_subquery()
        users = s.query(User).filter(User.age == subquery)
    return [{
        'id': user.id,
        'name': user.name,
        'surname': user.surname,
        'age': user.age,
    } for user in users]


@app.post('/register-user/', summary='CreateUser', response_model=UserModel)
def register_user(user: RegisterUserRequest):
    """
    Регистрация пользователя
    """
    user_object = User(**user.dict())
    s = Session()
    s.add(user_object)
    s.commit()

    return UserModel.from_orm(user_object)


@app.get('/all-picnics/', summary='All Picnics', tags=['picnic'])
def all_picnics(datetime: dt.datetime = Query(default=None, description='Время пикника (по умолчанию не задано)'),
                past: bool = Query(default=True, description='Включая уже прошедшие пикники')):
    """
    Список всех пикников
    """
    picnics = Session().query(Picnic)
    if datetime is not None:
        picnics = picnics.filter(Picnic.time == datetime)
    if not past:
        picnics = picnics.filter(Picnic.time >= dt.datetime.now())

    return [{
        'id': pic.id,
        'city': Session().query(City).filter(City.id == pic.id).first().name,
        'time': pic.time,
        'users': [
            {
                'id': pr.user.id,
                'name': pr.user.name,
                'surname': pr.user.surname,
                'age': pr.user.age,
            }
            for pr in Session().query(PicnicRegistration).filter(PicnicRegistration.picnic_id == pic.id)],
    } for pic in picnics]


@app.get('/picnic-add/', summary='Picnic Add', tags=['picnic'])
def picnic_add(city_id: int = None, datetime: dt.datetime = None):
    """
    Создет новый пикник в заданном городе
    """

    with Session() as s:
        subquery = s.query(City.id).filter(City.id == city_id)
        if not s.query(subquery.exists()).scalar():
            raise HTTPException(400, 'Города с заданным city_id не существует')

        p = Picnic(city_id=city_id, time=datetime)
        s.add(p)
        s.commit()

        return {
            'id': p.id,
            'city': p.city.name,
            'time': p.time,
        }


@app.get('/picnic-register/', summary='Picnic Registration', tags=['picnic'])
def register_to_picnic(user_id: int,
                       picnic_id: int):
    """
    Регистрация пользователя на пикник
    """
    with Session() as s:
        subquery = s.query(User.id).filter(User.id == user_id)
        if not s.query(subquery.exists()).scalar():
            raise HTTPException(400, 'Пользователя с заданным user_id не существует')

        subquery = s.query(Picnic.id).filter(Picnic.id == user_id)
        if not s.query(subquery.exists()).scalar():
            raise HTTPException(400, 'Пикника с заданным picnic_id не существует')

        picnic_registration_obj = PicnicRegistration(user_id=user_id,
                                                     picnic_id=picnic_id)
        s.add(picnic_registration_obj)
        s.commit()

        return {
            'id': picnic_registration_obj.id,
            'picnic': {
                'city': picnic_registration_obj.picnic.city.name,
                'time': picnic_registration_obj.picnic.time,
            },
            'user': {
                'name': picnic_registration_obj.user.name,
                'surname': picnic_registration_obj.user.surname,
                'age': picnic_registration_obj.user.age,
            }
        }


if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='127.0.0.1')
