"""索引基准测试"""
import pytest


@pytest.mark.asyncio
async def test_benchmark_no_index(client, auth_token, seed_item):
    """无索引基准查询"""
    response = await client.get("/api/v1/benchmark/no-index", headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "elapsed_ms" in data["data"]
    assert "plan" in data["data"]


@pytest.mark.asyncio
async def test_benchmark_with_index(client, auth_token, seed_item):
    """有索引基准查询"""
    response = await client.get("/api/v1/benchmark/with-index", headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "elapsed_ms" in data["data"]
    assert "plan" in data["data"]
