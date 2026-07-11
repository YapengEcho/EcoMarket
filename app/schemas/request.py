from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RequestCreate(BaseModel):
    item_id: int
    message: Optional[str] = None


class RequestUpdate(BaseModel):
    status: int  # 0:待处理 1:已接受 2:已拒绝 3:已完成


class RequestResponse(BaseModel):
    request_id: int
    item_id: int
    requester_id: int
    seller_id: int
    status: int
    message: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
