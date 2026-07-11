"""
EcoMarket - 智能⽣校园二手交易平台
FastAPI 入口

启动: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import db_manager, Base
from app.core.redis import check_redis_health
from app.api.v1 import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库和健康检查"""
    logger.info(f"🚀 {settings.app_name} 启动中...")

    # 初始化数据库引擎
    db_manager.ensure_initialized()

    # 异步健康检查
    await db_manager.check_health()
    await check_redis_health()

    # 自动创建表（开发/测试模式）
    if settings.db_strategy == "sqlite" or settings.debug:
        try:
            async with db_manager._engines[
                db_manager.get_active_db_type()
            ].begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ 数据库表已自动创建")
        except Exception as e:
            logger.warning(f"⚠️ 自动建表失败: {e}")

    logger.info(f"✅ {settings.app_name} 启动完成")
    yield

    # 关闭时清理
    await db_manager.close_all()
    logger.info(f"👋 {settings.app_name} 已关闭")


app = FastAPI(
    title=settings.app_name,
    description="基于 FastAPI + Qwen3.7-Plus 的智能校园二手交易平台",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(api_router)


# 静态文件（上传的图片）
import os
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }
