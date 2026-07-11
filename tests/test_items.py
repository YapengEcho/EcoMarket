"""商品模块测试"""
import pytest


@pytest.mark.asyncio
async def test_create_item(client, auth_token):
    """测试发布商品"""
    response = await client.post("/api/v1/items/", json={
        "title": "测试商品 - Python编程",
        "description": "几乎全新",
        "price": 30.00,
        "original_price": 59.00,
        "condition": 0,
    }, headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "item_id" in data["data"]


@pytest.mark.asyncio
async def test_get_item_detail(client, auth_token, seed_item):
    """测试获取商品详情"""
    response = await client.get(f"/api/v1/items/{seed_item.item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["title"] == "测试商品 - 高等数学第七版"
    assert data["data"]["price"] == 25.00


@pytest.mark.asyncio
async def test_get_item_not_found(client):
    """测试获取不存在的商品"""
    response = await client.get("/api/v1/items/99999")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 404


@pytest.mark.asyncio
async def test_search_items(client, auth_token, seed_item):
    """测试商品搜索"""
    response = await client.get("/api/v1/items/search", params={
        "keyword": "高等数学",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]["items"]) >= 1
    assert "query_time_ms" in data["data"]
    assert data["data"]["db_type"] == "sqlite"


@pytest.mark.asyncio
async def test_search_with_price_filter(client, auth_token, seed_item):
    """测试价格区间搜索"""
    response = await client.get("/api/v1/items/search", params={
        "min_price": 20,
        "max_price": 30,
    })
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]["items"]) >= 1


@pytest.mark.asyncio
async def test_update_item(client, auth_token, seed_item):
    """测试更新商品"""
    response = await client.put(f"/api/v1/items/{seed_item.item_id}", json={
        "title": "更新后的标题",
        "price": 35.00,
    }, headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200


@pytest.mark.asyncio
async def test_delete_item(client, auth_token, seed_item):
    """测试删除商品"""
    response = await client.delete(f"/api/v1/items/{seed_item.item_id}", headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200


@pytest.mark.asyncio
async def test_get_my_items(client, auth_token, seed_item):
    """测试获取我发布的商品"""
    response = await client.get("/api/v1/items/my/items", headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]) >= 1
