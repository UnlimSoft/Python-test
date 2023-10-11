from pydantic import BaseModel


class RegisterUserRequest(BaseModel):
    name: str
    surname: str
    age: int

    class Config:
        orm_mode = True


class UserModel(RegisterUserRequest):
    id: int

    class Config:
        orm_mode = True
