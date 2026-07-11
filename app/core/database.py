"""
双数据源管理器 - 支持 MySQL 主库 + openGauss 备库降级 + SQLite(测试/开发)

优化点（相对于原始 Plan）:
1. 不在 __init__ 中调用 asyncio.run()，避免 "event loop already running" 错误
2. 健康检查延迟到应用启动时 (lifespan) 异步执行
3. 新增 SQLite 策略，便于本地开发与单元测试
"""
import re
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from typing import Optional, Tuple, AsyncGenerator
import logging
from enum import Enum
from app.core.config import settings

logger = logging.getLogger(__name__)

# ==================== openGauss 版本兼容补丁 ====================
# openGauss 的 version() 返回类似 "openGauss-lite 7.0.0-RC1 build ..."
# 不符合 SQLAlchemy PostgreSQL 方言期望的标准格式，需要 monkey-patch
from sqlalchemy.dialects.postgresql.base import PGDialect

_original_get_server_version_info = PGDialect._get_server_version_info


def _patched_get_server_version_info(self, connection):
    try:
        return _original_get_server_version_info(self, connection)
    except (AssertionError, Exception):
        version_string = connection.exec_driver_sql("SELECT version()").scalar()
        match = re.search(r'(\d+)\.(\d+)\.(\d+)', str(version_string))
        if match:
            return tuple(int(x) for x in match.groups())
        return (13, 0, 0)


PGDialect._get_server_version_info = _patched_get_server_version_info
logger.debug("✅ openGauss 版本检测补丁已应用")

Base = declarative_base()


class DBType(str, Enum):
    MYSQL = "mysql"
    OPENGUASS = "opengauss"
    SQLITE = "sqlite"


class DatabaseManager:
    """双数据源管理器 - 支持 MySQL 主库 + openGauss 备库降级 + SQLite"""

    def __init__(self):
        self._engines = {}
        self._session_factories = {}
        self._active_db: Optional[DBType] = None
        self._mysql_healthy = False
        self._opengauss_healthy = False
        self._initialized = False

    def _init_engines(self):
        """初始化数据库引擎（延迟初始化，避免在导入时就连接）"""
        strategy = settings.db_strategy

        # SQLite 模式（开发/测试）
        if strategy == "sqlite":
            self._engines[DBType.SQLITE] = create_async_engine(
                settings.sqlite_database_url,
                echo=settings.debug,
                connect_args={"check_same_thread": False},
            )
            self._session_factories[DBType.SQLITE] = async_sessionmaker(
                self._engines[DBType.SQLITE], expire_on_commit=False
            )
            self._active_db = DBType.SQLITE
            self._initialized = True
            logger.info("✅ SQLite 引擎初始化完成 (开发/测试模式)")
            return

        # MySQL 引擎
        try:
            self._engines[DBType.MYSQL] = create_async_engine(
                settings.mysql_database_url,
                echo=settings.debug,
                pool_size=10,
                max_overflow=5,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            self._session_factories[DBType.MYSQL] = async_sessionmaker(
                self._engines[DBType.MYSQL], expire_on_commit=False
            )
            logger.info("✅ MySQL 引擎创建完成")
        except Exception as e:
            logger.warning(f"⚠️ MySQL 引擎创建失败: {e}")

        # openGauss 引擎
        try:
            self._engines[DBType.OPENGUASS] = create_async_engine(
                settings.opengauss_database_url,
                echo=settings.debug,
                pool_size=10,
                max_overflow=5,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            self._session_factories[DBType.OPENGUASS] = async_sessionmaker(
                self._engines[DBType.OPENGUASS], expire_on_commit=False
            )
            logger.info("✅ openGauss 引擎创建完成")
        except Exception as e:
            logger.warning(f"⚠️ openGauss 引擎创建失败: {e}")

        self._initialized = True
        # 选择活跃数据库（不进行健康检查，由 lifespan 负责）
        self._select_active_db_without_health()

    def _select_active_db_without_health(self):
        """在不做健康检查的情况下选择活跃数据库"""
        strategy = settings.db_strategy

        if strategy == "opengauss_only":
            self._active_db = DBType.OPENGUASS
            logger.info("📌 策略: 仅使用 openGauss")
            return

        if strategy == "primary":
            self._active_db = DBType.MYSQL
            logger.info("📌 策略: 仅使用 MySQL")
            return

        # fallback 策略：默认用 MySQL，运行时降级
        if strategy == "fallback":
            self._active_db = DBType.MYSQL
            logger.info("📌 策略: fallback | 默认使用 MySQL (主库)")
            return

    async def check_health(self):
        """异步健康检查（在应用启动时调用）"""
        if settings.db_strategy == "sqlite":
            self._active_db = DBType.SQLITE
            return

        if DBType.MYSQL in self._engines:
            try:
                async with self._engines[DBType.MYSQL].connect() as conn:
                    await conn.execute(text("SELECT 1"))
                self._mysql_healthy = True
                logger.info("✅ MySQL 健康检查通过")
            except Exception as e:
                self._mysql_healthy = False
                logger.warning(f"⚠️ MySQL 不可用: {e}")

        if DBType.OPENGUASS in self._engines:
            try:
                async with self._engines[DBType.OPENGUASS].connect() as conn:
                    await conn.execute(text("SELECT 1"))
                self._opengauss_healthy = True
                logger.info("✅ openGauss 健康检查通过")
            except Exception as e:
                self._opengauss_healthy = False
                logger.warning(f"⚠️ openGauss 不可用: {e}")

        # fallback 策略下根据健康状态调整
        if settings.db_strategy == "fallback":
            if not self._mysql_healthy and self._opengauss_healthy:
                self._active_db = DBType.OPENGUASS
                logger.warning("🔄 MySQL 不可用，已降级至 openGauss")
            elif not self._mysql_healthy and not self._opengauss_healthy:
                logger.error("❌ 所有数据库均不可用!")

    def ensure_initialized(self):
        """确保引擎已初始化（延迟初始化）"""
        if not self._initialized:
            self._init_engines()

    def get_active_db_type(self) -> DBType:
        self.ensure_initialized()
        if self._active_db is None:
            self._select_active_db_without_health()
        return self._active_db

    async def get_session_with_fallback(self) -> Tuple[AsyncSession, DBType]:
        """获取会话，如果当前数据库失败则尝试降级

        注意: 不在此处执行 SELECT 1 健康检查，因为会隐式开启事务，
        导致后续 db.begin() 冲突。连接健康由 pool_pre_ping=True 保证。
        """
        self.ensure_initialized()

        if self._active_db is None:
            raise RuntimeError("没有可用的数据库引擎")

        try:
            session = self._session_factories[self._active_db]()
            return session, self._active_db
        except Exception as e:
            logger.warning(f"当前数据库连接失败: {e}")
            # 尝试降级
            if self._active_db == DBType.MYSQL and DBType.OPENGUASS in self._engines:
                self._active_db = DBType.OPENGUASS
                logger.warning("🔄 已自动降级至 openGauss")
                session = self._session_factories[DBType.OPENGUASS]()
                return session, DBType.OPENGUASS
            raise

    async def close_all(self):
        """关闭所有引擎连接"""
        for db_type, engine in self._engines.items():
            try:
                await engine.dispose()
                logger.info(f"✅ {db_type.value} 引擎已关闭")
            except Exception as e:
                logger.warning(f"关闭 {db_type.value} 引擎失败: {e}")


db_manager = DatabaseManager()


# ==================== 依赖注入 ====================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """依赖注入: 获取数据库会话（带降级）"""
    session, db_type = await db_manager.get_session_with_fallback()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


def get_current_db_type() -> DBType:
    """获取当前数据库类型（用于兼容层）"""
    return db_manager.get_active_db_type()
