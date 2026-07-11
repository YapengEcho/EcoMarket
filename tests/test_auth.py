"""认证模块测试"""
import pytest


@pytest.mark.asyncio
async def test_register(client):
    """测试用户注册"""
    response = await client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "password": "pass123",
        "email": "new@test.com",
        "school": "测试大学",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["username"] == "newuser"
    assert "user_id" in data["data"]


@pytest.mark.asyncio
async def test_register_duplicate(client, test_user):
    """测试重复用户名注册"""
    response = await client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "password": "pass123",
    })
    data = response.json()
    assert data["code"] == 400
    assert "已存在" in data["message"]


@pytest.mark.asyncio
async def test_login_success(client):
    """测试登录成功"""
    # 先注册
    await client.post("/api/v1/auth/register", json={
        "username": "loginuser",
        "password": "pass123",
    })
    # 再登录
    response = await client.post("/api/v1/auth/login", json={
        "username": "loginuser",
        "password": "pass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "token" in data["data"]
    assert data["data"]["username"] == "loginuser"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """测试密码错误"""
    await client.post("/api/v1/auth/register", json={
        "username": "loginuser2",
        "password": "pass123",
    })
    response = await client.post("/api/v1/auth/login", json={
        "username": "loginuser2",
        "password": "wrongpass",
    })
    data = response.json()
    assert data["code"] == 401


@pytest.mark.asyncio
async def test_get_profile(client, auth_token):
    """测试获取个人信息"""
    response = await client.get("/api/v1/auth/me", headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["username"] == "testuser"
    assert data["data"]["reputation_score"] == 5.0


@pytest.mark.asyncio
async def test_get_profile_no_token(client):
    """测试无 token 访问"""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
