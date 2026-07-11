"""openGauss 初始化脚本：创建用户、数据库、表结构、索引"""
import asyncio
import sys
import os
import re
from urllib.parse import quote_plus
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# openGauss 版本字符串兼容补丁（与 app/core/database.py 保持一致）
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
print('✅ openGauss 版本检测补丁已应用')


async def main():
    admin_pwd = quote_plus('GaussIntelliShield@2024')
    admin_url = f"postgresql+asyncpg://gaussdb:{admin_pwd}@localhost:5432/postgres"

    # 1. 创建用户和数据库（用 gaussdb 管理员连接，使用 autocommit 模式）
    engine_admin = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    async with engine_admin.connect() as conn:
        # 检查用户是否存在，不存在则创建
        result = await conn.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = 'opengauss_user'")
        )
        if result.scalar():
            print('USER opengauss_user 已存在，跳过创建')
        else:
            await conn.execute(
                text("CREATE USER opengauss_user WITH PASSWORD 'og_pass123'")
            )
            print('USER opengauss_user created')

        # 检查数据库是否存在
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'ecomarket'")
        )
        if result.scalar():
            print('DATABASE ecomarket 已存在，跳过创建')
        else:
            await conn.execute(
                text('CREATE DATABASE ecomarket OWNER opengauss_user')
            )
            print('DATABASE ecomarket created')
    await engine_admin.dispose()

    # 2. 授予 opengauss_user 在 ecomarket 数据库的权限（用管理员连接到 ecomarket）
    engine_grant = create_async_engine(
        f"postgresql+asyncpg://gaussdb:{admin_pwd}@localhost:5432/ecomarket",
        isolation_level="AUTOCOMMIT"
    )
    async with engine_grant.connect() as conn:
        await conn.execute(text("GRANT ALL ON SCHEMA public TO opengauss_user"))
        await conn.execute(text("ALTER SCHEMA public OWNER TO opengauss_user"))
        print('✅ 已授予 opengauss_user 在 public schema 的权限')
    await engine_grant.dispose()

    # 3. 在 ecomarket 数据库上创建表结构
    from app.core.database import Base
    import app.models  # 确保所有模型被导入

    engine = create_async_engine(
        "postgresql+asyncpg://opengauss_user:og_pass123@localhost:5432/ecomarket"
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ TABLES created on openGauss')

    # 4. 创建 GIN 全文索引和其他索引
    async with engine.begin() as conn:
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ft_title_ts ON items USING gin(to_tsvector('english', title))"
        ))
        print('✅ FULLTEXT GIN index ft_title_ts created')
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_category_id ON items(category_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_status_price ON items(status, price)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_parent_id ON categories(parent_id)"))
        print('✅ 其他索引创建完成')

    await engine.dispose()
    print('\n🎉 openGauss 初始化完成！')


asyncio.run(main())
