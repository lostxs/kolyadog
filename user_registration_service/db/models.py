import uuid

from sqlalchemy import Column, UUID, String, DateTime, Boolean, func, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    is_active = Column(Boolean(), default=False)

    account_activation_codes = relationship(
        "ActivationCode", back_populates="user", uselist=False
    )


class ActivationCode(Base):
    __tablename__ = "account_activation_codes"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    code = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

    user = relationship("User", back_populates="account_activation_codes")
