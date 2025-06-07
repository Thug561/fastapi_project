from fastapi import FastAPI, HTTPException, Depends, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from starlette.middleware.cors import CORSMiddleware

from passlib.context import CryptContext

from jose import JWTError, jwt
from datetime import datetime, timedelta

from dotenv import load_dotenv
import os

load_dotenv()

# DATABASE_URL = "sqlite:///./test.db"
DATABASE_URL = "postgresql://ebook_db_y7e4_user:0xafHPKtkvidYg7wnRrOcJBOGafJ5SP1@dpg-d0kts17fte5s7390ss50-a:5432/ebook_db_y7e4"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

# --- PASSWORD HASHING UTILS ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- JWT CONFIG ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set in .env file")

# --- DATABASE MODEL ---
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

Base.metadata.create_all(bind=engine)

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

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- FASTAPI SETUP ---
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@app.post("/refresh", response_model=Token)
def refresh_access_token(token_request: RefreshTokenRequest):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token_request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- JWT HELPERS ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(db: Session, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# --- ROUTES ---

@app.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(
        (UserDB.username == user.username) | (UserDB.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    hashed_pwd = hash_password(user.password)
    new_user = UserDB(username=user.username, email=user.email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
@app.post("/token", response_model=dict)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: UserDB = Depends(get_current_user)):
    return current_user


# Приклад захищеного маршруту
@app.get("/protected-route")
async def protected_route(current_user: UserDB = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}. This is a protected route."}

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