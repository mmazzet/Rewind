async def test_register_success(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password_hash" not in data


async def test_register_existing_email(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "Email already registered"


async def test_register_short_password(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "123"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["detail"] == "Password must be at least 8 characters"


async def test_login_success(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password_hash" not in data


async def test_login_wrong_password(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "WrongPassword123"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"


async def test_login_nonexistent_email(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "Password123"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"


async def test_get_current_user_success(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Password123"},
    )

    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 200


async def test_get_current_user_without_cookie(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_logout(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Password123"},
    )
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 204
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
