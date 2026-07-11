from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FavoriteCreate(BaseModel):
    item_id: int


class FavoriteResponse(BaseModel):
    favorite_id: int
    user_id: int
    item_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
