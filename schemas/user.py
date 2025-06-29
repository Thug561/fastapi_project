from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class User(BaseModel):
    id: int
    username: str
    email: str

class Config:
    orm_mode = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[constr(min_length=6)] = None