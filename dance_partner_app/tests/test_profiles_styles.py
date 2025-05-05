import pytest
from httpx import AsyncClient
from fastapi import status
import random
import string

async def get_auth_headers(client: AsyncClient, email: str = None, password: str = "testpassword") -> dict:
    if email is None:
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email = f"test_profile_user_{random_suffix}@example.com"

    await client.post("/users/", json={"email": email, "password": password})

    login_response = await client.post("/auth/token", data={"username": email, "password": password})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers

# --- Dance Style Tests --- #

@pytest.mark.asyncio
async def test_create_dance_style(client: AsyncClient):
    """Тестирует успешное создание танцевального стиля."""
    style_name = "Test Style Salsa"
    response = await client.post(
        "/styles/",
        json={"name": style_name, "description": "A test style"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == style_name
    assert data["description"] == "A test style"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_duplicate_dance_style(client: AsyncClient):
    """Тестирует создание стиля с уже существующим именем."""
    style_name = "Duplicate Test Style"
    await client.post("/styles/", json={"name": style_name, "description": "First"})
    response = await client.post("/styles/", json={"name": style_name, "description": "Second"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert f"'{style_name}' already exists" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_dance_styles(client: AsyncClient):
    """Тестирует получение списка стилей."""
    await client.post("/styles/", json={"name": "Style List Test 1"})
    await client.post("/styles/", json={"name": "Style List Test 2"})

    response = await client.get("/styles/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    if data:
        assert "id" in data[0]
        assert "name" in data[0]

@pytest.mark.asyncio
async def test_get_dance_style_by_id(client: AsyncClient):
    """Тестирует получение стиля по ID."""
    style_name = "Style By ID Test"
    create_response = await client.post("/styles/", json={"name": style_name})
    style_id = create_response.json()["id"]

    response = await client.get(f"/styles/{style_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == style_id
    assert data["name"] == style_name

@pytest.mark.asyncio
async def test_get_nonexistent_dance_style(client: AsyncClient):
    """Тестирует получение несуществующего стиля."""
    response = await client.get("/styles/999999") # Маловероятно, что такой ID будет
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Dance style not found"

# --- Profile Tests --- #

@pytest.mark.asyncio
async def test_get_my_profile_not_found(client: AsyncClient):
    """Тестирует получение профиля, когда он еще не создан."""
    headers = await get_auth_headers(client, email="profile_notfound@example.com")
    response = await client.get("/profiles/me", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Profile not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_my_profile(client: AsyncClient):
    """Тестирует создание профиля текущего пользователя."""
    headers = await get_auth_headers(client, email="createprofile@example.com")
    profile_data = {"first_name": "Test", "last_name": "User", "city": "Test City"}

    response = await client.put("/profiles/me", json=profile_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert data["city"] == "Test City"
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "dance_styles" in data and isinstance(data["dance_styles"], list)

@pytest.mark.asyncio
async def test_update_my_profile(client: AsyncClient):
    """Тестирует обновление профиля текущего пользователя."""
    email = "updateprofile@example.com"
    headers = await get_auth_headers(client, email=email)
    # Сначала создаем профиль
    await client.put("/profiles/me", json={"first_name": "Initial", "city": "Old City"}, headers=headers)

    # Обновляем профиль
    update_data = {"first_name": "Updated", "bio": "New Bio"}
    response = await client.put("/profiles/me", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "Updated" # Имя обновилось
    assert data["city"] == "Old City"      # Город остался прежним (не передавали в update_data)
    assert data["bio"] == "New Bio"        # Bio добавилось

@pytest.mark.asyncio
async def test_get_my_profile_exists(client: AsyncClient):
    """Тестирует получение существующего профиля."""
    email = "getmyprofile@example.com"
    headers = await get_auth_headers(client, email=email)
    # Создаем профиль
    create_response = await client.put("/profiles/me", json={"city": "Profile City"}, headers=headers)
    profile_id = create_response.json()["id"]

    # Получаем профиль
    response = await client.get("/profiles/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == profile_id
    assert data["city"] == "Profile City"

@pytest.mark.asyncio
async def test_get_profile_by_id(client: AsyncClient):
    """Тестирует получение чужого профиля по ID (публичный доступ)."""
    # Создаем пользователя и его профиль
    headers = await get_auth_headers(client, email="publicprofile@example.com")
    create_response = await client.put("/profiles/me", json={"city": "Public City"}, headers=headers)
    profile_id = create_response.json()["id"]

    # Запрашиваем профиль без авторизации (или от другого пользователя)
    response = await client.get(f"/profiles/{profile_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == profile_id
    assert data["city"] == "Public City"

@pytest.mark.asyncio
async def test_get_nonexistent_profile_by_id(client: AsyncClient):
    """Тестирует получение несуществующего профиля по ID."""
    response = await client.get("/profiles/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Profile not found" 
