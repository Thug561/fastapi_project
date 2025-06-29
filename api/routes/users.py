from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.models import UserDB
from schemas.user import User, UserCreate, UserUpdate
from core.security import hash_password
from api.deps import get_db, get_current_user

router = APIRouter()

@router.put("/me", response_model=User)
async def update_current_user(
    update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    if update.username and update.username != current_user.username:
        existing_user = db.query(UserDB).filter(UserDB.username == update.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = update.username

    if update.password:
        current_user.hashed_password = hash_password(update.password)

    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
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

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: UserDB = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=list[User])
def get_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User with id {user_id} deleted"}

@router.get("/users/count")
def count_users(db: Session = Depends(get_db)):
    return {"count": db.query(UserDB).count()}

@router.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = updated_user.username
    user.email = updated_user.email
    db.commit()
    db.refresh(user)
    return user