"""
测试配置 - 使用 SQLite 内存数据库，每个测试函数独立隔离

运行测试: pytest tests/ -v
"""
import asyncio
import os
import sys

# 设置环境变量为 sqlite 模式（必须在导入 app 之前）
os.environ["DB_STRATEGY"] = "sqlite"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DEBUG"] = "False"

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import db_manager, Base, DBType
from app.core.security import hash_password, create_access_token, decode_token
from app.models.user import User
from app.models.item import Item
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_engine():
    """每个测试函数使用独立的内存数据库"""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """数据库会话"""
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        await session.close()


@pytest_asyncio.fixture
async def client(test_engine, db_session):
    """测试客户端 - 覆盖 get_db 依赖"""
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            await session.close()

    from app.core.database import get_db
    app.dependency_overrides[get_db] = override_get_db

    # 设置 db_manager 使用测试引擎
    db_manager._engines[DBType.SQLITE] = test_engine
    db_manager._session_factories[DBType.SQLITE] = session_factory
    db_manager._active_db = DBType.SQLITE
    db_manager._initialized = True

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    """创建测试用户并返回用户对象"""
    user = User(
        username="testuser",
        password_hash=hash_password("testpass123"),
        email="test@test.com",
        school="测试大学",
        reputation_score=5.00,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user2(db_session):
    """创建第二个测试用户"""
    user = User(
        username="testuser2",
        password_hash=hash_password("testpass456"),
        email="test2@test.com",
        school="测试大学",
        reputation_score=5.00,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_token(test_user):
    """返回 test_user 的 JWT token"""
    token = create_access_token(
        {"user_id": test_user.user_id, "username": "testuser"}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def second_token(test_user2):
    """返回 test_user2 的 JWT token"""
    token = create_access_token(
        {"user_id": test_user2.user_id, "username": "testuser2"}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def seed_item(db_session, test_user):
    """创建测试商品"""
    item = Item(
        user_id=test_user.user_id,
        title="测试商品 - 高等数学第七版",
        description="同济大学版，九成新",
        price=25.00,
        original_price=49.80,
        condition=0,
        status=0,
    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    return item
