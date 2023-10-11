import datetime as dt
from typing import Optional, List

from pydantic import BaseModel, Field

from .users import UserModel, RegisterUserRequest


class NewPicnicRequest(BaseModel):
    city_id: Optional[str] = Field(None, description='id города, в котором будет пикник')
    datetime: Optional[dt.datetime] = Field(None, description='Время проведения пикника')


class PicnicMin(BaseModel):
    city: str
    time: dt.datetime

    class Config:
        orm_mode = True


class PicnicResponse(PicnicMin):
    id: int

    class Config:
        orm_mode = True


class PicnicResponseExtended(PicnicResponse):
    users: List[UserModel] = Field([], description='Список зарегестрированных пользователей')

    class Config:
        orm_mode = True


class PicnicRegistrationResponse(BaseModel):
    id: int
    picnic: PicnicMin
    user: RegisterUserRequest

    class Config:
        orm_mode = True


class PicnicRegistrationRequest(BaseModel):
    user_id: int
    picnic_id: int
