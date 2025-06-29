from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .session import Base
import enum

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class FriendRequestStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"

class FriendRequest(Base):
    __tablename__ = "friend_requests"

    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    to_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    status = Column(Enum(FriendRequestStatus), default=FriendRequestStatus.pending, nullable=False)

    from_user = relationship("UserDB", foreign_keys=[from_user_id])
    to_user = relationship("UserDB", foreign_keys=[to_user_id])
