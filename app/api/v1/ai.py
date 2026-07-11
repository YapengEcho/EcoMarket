from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.ai_service import Qwen37PlusService
from app.core.security import get_current_user
from app.utils.response import success, error

router = APIRouter(prefix="/ai", tags=["AI"])


class GenerateRequest(BaseModel):
    product_name: str
    additional_info: Optional[str] = None


@router.post("/generate")
async def ai_generate_item(
    req: GenerateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Qwen3.7-Plus 智能生成商品信息
    输入商品名称，AI 生成建议售价和卖点描述
    """
    result = await Qwen37PlusService.generate_item_info(
        req.product_name, req.additional_info
    )

    if result.get("error"):
        return error(result["error"], 500)

    return success(result, "AI 生成成功")


@router.post("/search")
async def ai_search(
    query: str,
    current_user: dict = Depends(get_current_user),
):
    """Qwen3.7-Plus 智能搜索"""
    result = await Qwen37PlusService.search_with_web(query)
    return success({"result": result})
