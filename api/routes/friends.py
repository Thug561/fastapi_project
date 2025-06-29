from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from schemas.friends import FriendRequestCreate, FriendRequestResponse, FriendRequestStatus
from crud.friend_requests import send_friend_request, respond_to_friend_request, get_pending_requests, get_friends
from api.deps import get_db, get_current_user
from database.models import UserDB, FriendRequest

router = APIRouter(prefix="/friends", tags=["friends"])

@router.post("/request", response_model=FriendRequestResponse)
def create_friend_request(request: FriendRequestCreate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    if request.to_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
    friend_request = send_friend_request(db, current_user.id, request.to_user_id)
    if not friend_request:
        raise HTTPException(status_code=400, detail="Friend request already sent")
    return friend_request

@router.post("/request/{request_id}/respond", response_model=FriendRequestResponse)
def respond_friend_request(request_id: int, accept: bool, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    friend_request = db.query(FriendRequest).filter(FriendRequest.id == request_id, FriendRequest.to_user_id == current_user.id).first()
    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")
    updated_request = respond_to_friend_request(db, request_id, accept)
    return updated_request

@router.get("/requests", response_model=List[FriendRequestResponse])
def list_pending_requests(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    return get_pending_requests(db, current_user.id)

@router.get("/", response_model=List[FriendRequestResponse])
def list_friends(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    return get_friends(db, current_user.id)
