from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from starlette.middleware.cors import CORSMiddleware

# DATABASE_URL = "sqlite:///./test.db"
DATABASE_URL = "postgresql://ebook_db_y7e4_user:0xafHPKtkvidYg7wnRrOcJBOGafJ5SP1@dpg-d0kts17fte5s7390ss50-a:5432/ebook_db_y7e4"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)

Base.metadata.create_all(bind=engine)

class User(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI on Render!"}


@app.post("/users", response_model=User)
def create_user(user: User, db: Session = Depends(get_db)):
    new_user = UserDB(username=user.username, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users", response_model=List[User])
def get_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = updated_user.username
    user.email = updated_user.email
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User with id {user_id} deleted"}

@app.get("/users/count")
def count_users(db: Session = Depends(get_db)):
    return {"count": db.query(UserDB).count()}