import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_user_registration(client: AsyncClient):
    """Тестирует успешную регистрацию пользователя."""
    response = await client.post(
        "/users/",
        json={"email": "testuser@example.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data
    assert data["is_active"] is True
    # Убедимся, что пароль не возвращается
    assert "hashed_password" not in data
    assert "password" not in data

@pytest.mark.asyncio
async def test_register_existing_user(client: AsyncClient):
    """Тестирует регистрацию пользователя с уже существующим email."""
    # Сначала регистрируем пользователя
    await client.post(
        "/users/",
        json={"email": "existing@example.com", "password": "password123"}
    )
    # Пытаемся зарегистрировать снова с тем же email
    response = await client.post(
        "/users/",
        json={"email": "existing@example.com", "password": "anotherpassword"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_for_access_token(client: AsyncClient):
    """Тестирует успешный логин и получение токена."""
    # Сначала регистрируем пользователя
    email = "loginuser@example.com"
    password = "loginpass"
    await client.post("/users/", json={"email": email, "password": password})

    # Пытаемся залогиниться
    login_data = {"username": email, "password": password}
    response = await client.post("/auth/token", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Тестирует логин с неверным паролем."""
    email = "wrongpass@example.com"
    password = "correctpass"
    await client.post("/users/", json={"email": email, "password": password})

    login_data = {"username": email, "password": "incorrectpass"}
    response = await client.post("/auth/token", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"

@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Тестирует логин несуществующего пользователя."""
    login_data = {"username": "nonexistent@example.com", "password": "password"}
    response = await client.post("/auth/token", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_read_users_me_unauthorized(client: AsyncClient):
    """Тестирует доступ к /users/me без авторизации."""
    response = await client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_read_users_me_authorized(client: AsyncClient):
    """Тестирует доступ к /users/me с авторизацией."""
    # Регистрация и логин
    email = "me_user@example.com"
    password = "me_pass"
    reg_response = await client.post("/users/", json={"email": email, "password": password})
    user_id = reg_response.json()["id"]

    login_response = await client.post("/auth/token", data={"username": email, "password": password})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Запрос к /users/me с токеном
    response = await client.get("/users/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == email
    assert data["id"] == user_id
    assert data["is_active"] is True 
