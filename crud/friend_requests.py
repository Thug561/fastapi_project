from sqlalchemy.orm import Session
from database.models import FriendRequest, FriendRequestStatus

def send_friend_request(db: Session, from_user_id: int, to_user_id: int):
    existing = db.query(FriendRequest).filter(
        FriendRequest.from_user_id == from_user_id,
        FriendRequest.to_user_id == to_user_id,
        FriendRequest.status == FriendRequestStatus.pending
    ).first()
    if existing:
        return None

    friend_request = FriendRequest(
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        status=FriendRequestStatus.pending
    )
    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)
    return friend_request

def respond_to_friend_request(db: Session, request_id: int, accept: bool):
    friend_request = db.query(FriendRequest).filter(FriendRequest.id == request_id).first()
    if not friend_request:
        return None
    friend_request.status = FriendRequestStatus.accepted if accept else FriendRequestStatus.declined
    db.commit()
    db.refresh(friend_request)
    return friend_request

def get_pending_requests(db: Session, user_id: int):
    return db.query(FriendRequest).filter(
        FriendRequest.to_user_id == user_id,
        FriendRequest.status == FriendRequestStatus.pending
    ).all()

def get_friends(db: Session, user_id: int):
    accepted = db.query(FriendRequest).filter(
        ((FriendRequest.from_user_id == user_id) | (FriendRequest.to_user_id == user_id)) &
        (FriendRequest.status == FriendRequestStatus.accepted)
    ).all()
    return accepted
