from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    username: str
    email: str

fake_users_db = []

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI on Render!"}

@app.post("/users")
def create_user(user: User):
    fake_users_db.append(user)
    return {"message": "User created", "user": user}

@app.get("/users")
def get_users():
    return fake_users_db