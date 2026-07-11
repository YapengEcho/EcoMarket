from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Request(Base):
    __tablename__ = "requests"

    request_id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    item_id = Column(BigInteger, ForeignKey("items.item_id"), nullable=False)
    requester_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    seller_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    status = Column(Integer, default=0)  # 0:待处理 1:已接受 2:已拒绝 3:已完成
    message = Column(String(500), nullable=True)
    # 交易码：卖家接受时生成的 6 位数字，买家线下输码确认收货
    trade_code = Column(String(6), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    item = relationship("Item", back_populates="requests", foreign_keys=[item_id])

    __table_args__ = (
        Index("idx_item_status", "item_id", "status"),
        Index("idx_requester", "requester_id"),
        Index("idx_seller", "seller_id"),
    )
