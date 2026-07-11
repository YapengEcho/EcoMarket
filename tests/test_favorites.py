"""收藏模块测试"""
import pytest


@pytest.mark.asyncio
async def test_add_favorite(client, auth_token, seed_item):
    """测试收藏商品"""
    response = await client.post(
        "/api/v1/favorites/",
        json={"item_id": seed_item.item_id},
        headers=auth_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "favorite_id" in data["data"]


@pytest.mark.asyncio
async def test_add_favorite_duplicate(client, auth_token, seed_item):
    """测试重复收藏"""
    await client.post("/api/v1/favorites/", json={"item_id": seed_item.item_id}, headers=auth_token)
    response = await client.post(
        "/api/v1/favorites/",
        json={"item_id": seed_item.item_id},
        headers=auth_token,
    )
    data = response.json()
    assert data["code"] == 400


@pytest.mark.asyncio
async def test_list_favorites(client, auth_token, seed_item):
    """测试获取收藏列表"""
    await client.post("/api/v1/favorites/", json={"item_id": seed_item.item_id}, headers=auth_token)
    response = await client.get("/api/v1/favorites/", headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]) >= 1
    assert data["data"][0]["title"] == "测试商品 - 高等数学第七版"


@pytest.mark.asyncio
async def test_remove_favorite(client, auth_token, seed_item):
    """测试取消收藏"""
    await client.post("/api/v1/favorites/", json={"item_id": seed_item.item_id}, headers=auth_token)
    response = await client.delete(
        f"/api/v1/favorites/{seed_item.item_id}", headers=auth_token
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
