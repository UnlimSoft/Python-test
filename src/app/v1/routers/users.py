from typing import Optional, List

from fastapi import APIRouter, Query

from db import User, Session
from ..models.users import RegisterUserRequest, UserModel

router = APIRouter(prefix='/users', tags=['Users'])


@router.post('/create/', summary='Create user', response_model=UserModel)
def register_user(user: RegisterUserRequest):
    """
    Регистрация пользователя
    """
    user_object = User(**user.dict())
    s = Session()
    s.add(user_object)
    s.commit()

    return UserModel.from_orm(user_object)


@router.get('/get/', summary='List users', response_model=List[UserModel])
def users_list(min_age: Optional[int] = Query(description="Минимальный возраст", default=None, gt=0),
               max_age: Optional[int] = Query(description="Максимальный возраст", default=None)):
    """
    Список пользователей
    """

    min_age, max_age = min(min_age, max_age), max(min_age, max_age)  # гарантируем, что min_age <= max_age

    users = Session().query(User)
    if min_age:
        users = users.filter(User.age >= min_age)
    if max_age:
        users = users.filter(User.age <= max_age)

    return [UserModel.from_orm(user) for user in users.all()]
