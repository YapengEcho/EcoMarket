from sqlalchemy import Column, BigInteger, Integer, String, Boolean, DateTime, Index, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    msg_id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    sender_id = Column(BigInteger, nullable=False)
    receiver_id = Column(BigInteger, nullable=False)
    # item_id 关联商品，用于基于商品的对话（系统通知可为 NULL）
    item_id = Column(BigInteger, ForeignKey("items.item_id"), nullable=True)
    title = Column(String(100), nullable=True)
    content = Column(String(1000), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_receiver_read", "receiver_id", "is_read"),
        Index("idx_item_messages", "item_id"),
    )
