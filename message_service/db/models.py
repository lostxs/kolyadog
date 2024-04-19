import uuid

from sqlalchemy import Column, UUID, Integer, func, DateTime, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=False)

    messages = relationship("Message", back_populates="user")
    connection_history = relationship("ConnectionHistory", back_populates="user")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    user = relationship("User", back_populates="messages")


class ConnectionHistory(Base):
    __tablename__ = "connection_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    connected_at = Column(DateTime(timezone=True), default=func.now())
    disconnected_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="connection_history")
