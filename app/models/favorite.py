from sqlalchemy import Column, BigInteger, Integer, DateTime, Index, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    favorite_id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    item_id = Column(BigInteger, ForeignKey("items.item_id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_user_item"),
        Index("idx_favorite_user", "user_id"),
    )
