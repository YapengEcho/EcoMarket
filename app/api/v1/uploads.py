from fastapi import APIRouter, Depends, UploadFile, File
from app.core.security import get_current_user
from app.utils.upload import save_upload_file
from app.utils.response import success, error

router = APIRouter(prefix="/uploads", tags=["上传"])


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """上传商品图片，返回访问 URL"""
    try:
        url = await save_upload_file(file)
        return success({"url": url}, "上传成功")
    except Exception as e:
        return error(str(e), 400)
