"""交易模块测试"""
import pytest


@pytest.mark.asyncio
async def test_create_request(client, auth_token, second_token, seed_item):
    """测试发起交易请求"""
    response = await client.post("/api/v1/requests/", json={
        "item_id": seed_item.item_id,
        "message": "我想要这个商品",
    }, headers=second_token)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "request_id" in data["data"]


@pytest.mark.asyncio
async def test_create_request_own_item(client, auth_token, seed_item):
    """测试购买自己发布的商品（应失败）"""
    response = await client.post("/api/v1/requests/", json={
        "item_id": seed_item.item_id,
    }, headers=auth_token)
    data = response.json()
    assert data["code"] == 400
    assert "自己" in data["message"]


@pytest.mark.asyncio
async def test_update_request_status(client, auth_token, second_token, seed_item):
    """测试更新交易状态（卖家接受）"""
    # 买家发起请求
    resp = await client.post("/api/v1/requests/", json={
        "item_id": seed_item.item_id,
    }, headers=second_token)
    request_id = resp.json()["data"]["request_id"]

    # 卖家接受
    response = await client.put(
        f"/api/v1/requests/{request_id}/status",
        params={"status": 1},
        headers=auth_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["status"] == 1


@pytest.mark.asyncio
async def test_complete_transaction(client, auth_token, second_token, seed_item):
    """测试完成交易全流程"""
    # 1. 买家发起请求
    resp = await client.post("/api/v1/requests/", json={
        "item_id": seed_item.item_id,
    }, headers=second_token)
    request_id = resp.json()["data"]["request_id"]

    # 2. 卖家接受
    await client.put(
        f"/api/v1/requests/{request_id}/status",
        params={"status": 1},
        headers=auth_token,
    )

    # 3. 买家确认完成
    response = await client.put(
        f"/api/v1/requests/{request_id}/status",
        params={"status": 3},
        headers=second_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["status"] == 3


@pytest.mark.asyncio
async def test_get_my_requests(client, auth_token, second_token, seed_item):
    """测试获取我的交易列表"""
    # 发起交易
    await client.post("/api/v1/requests/", json={
        "item_id": seed_item.item_id,
    }, headers=second_token)

    # 查看买家交易列表
    response = await client.get("/api/v1/requests/my", headers=second_token)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]) >= 1

    # 查看卖家交易列表
    response = await client.get(
        "/api/v1/requests/my",
        params={"as_buyer": False},
        headers=auth_token,
    )
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]) >= 1
