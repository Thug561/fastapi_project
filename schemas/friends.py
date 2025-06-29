from pydantic import BaseModel
from enum import Enum

class FriendRequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"

class FriendRequestBase(BaseModel):
    to_user_id: int

class FriendRequestCreate(FriendRequestBase):
    pass

class FriendRequestResponse(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    status: FriendRequestStatus

    class Config:
        orm_mode = True
