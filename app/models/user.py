from sqlalchemy import Column, BigInteger, Integer, String, DECIMAL, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(20), unique=True, nullable=True)
    avatar = Column(String(255), nullable=True)
    school = Column(String(100), nullable=True)
    reputation_score = Column(DECIMAL(3, 2), default=5.00)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    items = relationship("Item", back_populates="user", foreign_keys="Item.user_id")

    __table_args__ = (
        Index("idx_username", "username"),
        Index("idx_email", "email"),
    )
