from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:5173/ebook",
    "https://aitishnitsa.github.io",
    "https://aitishnitsa.github.io/ebook",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    id: int
    username: str
    email: str

users_db = [
    User(id=1, username="Dima Loadin...", email="test1@example.com"),
    User(id=2, username="Vitaliy Jsonc", email="test2@example.com"),
    User(id=3, username="Vertex Queen", email="test3@example.com"),
]

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI on Render!"}

@app.post("/users")
def create_user(user: User):
    users_db.append(user)
    return {"message": "User created", "user": user}

@app.get("/users", response_model=List[User])
def get_users():
    return users_db