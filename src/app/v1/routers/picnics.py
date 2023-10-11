import datetime as dt
from typing import List

from fastapi import APIRouter, Query

from db import Session, Picnic, User, PicnicRegistration, City
from utils import exceptions
from ..models.picnics import NewPicnicRequest, PicnicResponse, PicnicResponseExtended, PicnicRegistrationResponse, \
    PicnicRegistrationRequest

router = APIRouter(prefix='/picnics', tags=['Picnics'])


@router.post('/create/', summary='Picnic Add', response_model=PicnicResponse)
def picnic_add(picnic: NewPicnicRequest):
    """
    Создет новый пикник в заданном городе
    """

    with Session() as s:
        subquery = s.query(City.id).filter(City.id == picnic.city_id)
        if not s.query(subquery.exists()).scalar():
            raise exceptions.RecordDoesntExistException('city_id', picnic.city_id)

        p = Picnic(city_id=picnic.city_id, time=picnic.datetime)
        s.add(p)
        s.commit()

        return PicnicResponse.from_orm(p)


@router.get('/get/', summary='All Picnics', response_model=List[PicnicResponseExtended])
def get_picnics(datetime: dt.datetime = Query(default=None, description='Время пикника (по умолчанию не задано)'),
                past: bool = Query(default=True, description='Включая уже прошедшие пикники')):
    """
    Список всех пикников
    """
    with Session() as session:

        picnics = session.query(Picnic, User, City)

        if datetime is not None:
            picnics = picnics.filter(Picnic.time == datetime)
        if not past:
            picnics = picnics.filter(Picnic.time >= dt.datetime.now())
        picnics = (picnics.outerjoin(PicnicRegistration, Picnic.id == PicnicRegistration.picnic_id)
                   .outerjoin(User, PicnicRegistration.user_id == User.id)
                   .outerjoin(City, City.id == Picnic.city_id))
        session.commit()

    return_list = list()
    picnic_processed = list()
    for pic, user, city in picnics:
        if pic.id in picnic_processed:
            continue

        # я устал пытаться приветсти данные с ДБ к модели без явного указания полей. Пусть будет так
        return_list.append(PicnicResponseExtended(city=pic.city,
                                                  time=pic.time,
                                                  id=pic.id,
                                                  users=[reg.user for reg in pic.users]))
        picnic_processed.append(pic.id)
    return return_list


@router.post('/register/', summary='Picnic Registration', response_model=PicnicRegistrationResponse)
def register_to_picnic(registration: PicnicRegistrationRequest):
    """
    Регистрация пользователя на пикник
    """
    with Session() as s:
        subquery = s.query(User.id).filter(User.id == registration.user_id)
        if not s.query(subquery.exists()).scalar():
            raise exceptions.RecordDoesntExistException('user_id', registration.user_id)

        subquery = s.query(Picnic.id).filter(Picnic.id == registration.picnic_id)
        if not s.query(subquery.exists()).scalar():
            raise exceptions.RecordDoesntExistException('picnic_id', registration.picnic_id)

        picnic_registration_obj = PicnicRegistration(user_id=registration.user_id,
                                                     picnic_id=registration.picnic_id)
        s.add(picnic_registration_obj)
        s.commit()

        return PicnicRegistrationResponse.from_orm(picnic_registration_obj)
