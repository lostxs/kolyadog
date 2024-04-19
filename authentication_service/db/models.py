from sqlalchemy import Column, UUID, String, DateTime, Boolean, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AuthUser(Base):
    __tablename__ = "auth_users"

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
