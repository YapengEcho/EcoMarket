import os
import uuid
from fastapi import UploadFile, HTTPException
from app.core.config import settings


async def save_upload_file(file: UploadFile) -> str:
    """保存上传文件，返回文件 URL 路径"""
    # 检查文件大小
    content = await file.read()
    if len(content) > settings.max_upload_size:
        raise HTTPException(status_code=400, detail="文件大小超过限制")

    # 检查文件扩展名
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    # 确保上传目录存在
    upload_dir = settings.upload_dir
    os.makedirs(upload_dir, exist_ok=True)

    # 生成唯一文件名
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    return f"/uploads/{filename}"
