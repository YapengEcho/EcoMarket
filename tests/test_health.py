"""健康检查和系统测试"""
import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """测试健康检查"""
    response = await client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["active_db"] == "sqlite"
    assert data["app"] == "EcoMarket"


@pytest.mark.asyncio
async def test_db_status(client):
    """测试数据库状态"""
    response = await client.get("/api/v1/health/db-status")
    assert response.status_code == 200
    data = response.json()
    assert data["active_db"] == "sqlite"
    assert "databases" in data


@pytest.mark.asyncio
async def test_root(client):
    """测试根路由"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "EcoMarket"
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_statistics_dashboard(client, auth_token, seed_item):
    """测试数据看板"""
    response = await client.get("/api/v1/statistics/dashboard", headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "overview" in data["data"]
    assert data["data"]["overview"]["total_items"] >= 1
    assert "categories" in data["data"]
    assert "price_ranges" in data["data"]
