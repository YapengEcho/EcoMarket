from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, Integer, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Item(Base):
    __tablename__ = "items"

    item_id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    original_price = Column(DECIMAL(10, 2), nullable=True)
    condition = Column(Integer, default=0)  # 0:全新 1:闲置
    status = Column(Integer, default=0)  # 0:在售 1:已预订 2:已售出
    images = Column(String(1000), nullable=True)
    latitude = Column(DECIMAL(10, 7), nullable=True)
    longitude = Column(DECIMAL(10, 7), nullable=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="items", foreign_keys=[user_id])
    requests = relationship("Request", back_populates="item", foreign_keys="Request.item_id")

    __table_args__ = (
        Index("idx_status_time", "status", "created_at"),
        Index("idx_status_time_cover", "status", "created_at", "title", "price"),
        Index("idx_user_id", "user_id"),
        Index("idx_category_id", "category_id"),
        Index("idx_status_price", "status", "price"),
    )
