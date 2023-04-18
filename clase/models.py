from pydantic import BaseModel
from typing import Union
from datetime import datetime

class CompanyBase(BaseModel):

    commercial: Union[str, None] = None
    fiscal: Union[str, None] = None
    vat: Union[str, None] = None
    active: Union[bool, None] = None
    class Config:
        orm_mode = True

class CompanyCreate(CompanyBase):
    created: datetime
    updated: datetime

class Company(CompanyBase):
    id: int
    created: datetime
    updated: datetime


class UserBase(BaseModel):
    
    name: Union[str, None] = None
    email: Union[str, None] = None
    phone: Union[str, None] = None
    active: Union[bool, None] = None
    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: Union[str, None] = None
    company: Union[int, None] = None
    admin: Union[bool, None] = False
    super: Union[bool, None] = False
    created: datetime
    updated: datetime

class User(UserBase):
    id: int
    company: Union[CompanyBase, None] = None
    created: datetime
    updated: datetime
    
class MovementBase(BaseModel):
    code: Union[str, None] = None
    description: Union[str, None] = None
    active: Union[bool, None] = None
    class Config:
        orm_mode = True
    
class MovementCreate(MovementBase):
    created: datetime
    updated: datetime

class Movement(MovementBase):
    id: int
    created: datetime
    updated: datetime

class SignBase(BaseModel):
    user: Union[UserBase, None] = None
    login: datetime
    movement: Union[MovementBase, None] = None
    location: Union[str, None] = None
    identifier: Union[str, None] = None
    class Config:
        orm_mode = True
    
class SignCreate(SignBase):
    created: datetime
    updated: datetime

class Sign(SignBase):
    id: int
    created: datetime
    updated: datetime

class Login(BaseModel):
    email: Union[str, None] = None
    password: Union[str, None] = None

class LoginCheck(BaseModel):
    user_id : Union[int, None] = None
    company_id : Union[int, None] = None

class Token(BaseModel):
    access_token: Union[str, None] = None

class SimpleUser(BaseModel):
    id: int           
    name: Union[str, None] = None
    isActive: Union[bool, None] = None
    created: datetime
    updated: datetime
    class Config:
        orm_mode = True

class SimpleLog(BaseModel):
    id: int 
    login: datetime
    action: Union[str, None] = None
    comment: Union[str, None] = None
    longitude: Union[str, None] = None
    latitude: Union[str, None] = None
    proof: Union[str, None] = None
    class Config:
        orm_mode = True

class SimpleLogCreate(SimpleLog):
       user: Union[int, None] = None

class SimpleLogGet(SimpleLog):
    user: Union[SimpleUser, None] = None

class SimplePass(BaseModel):
    id: int
    token: Union[str, None] = None
    