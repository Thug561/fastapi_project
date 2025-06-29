from pydantic import BaseModel, EmailStr

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