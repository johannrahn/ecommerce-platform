def test_register(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "securepass123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert data["role"] == "customer"
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    payload = {
        "email": "dup@example.com",
        "password": "pass123",
        "full_name": "User",
    }
    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "login@example.com",
            "password": "mypassword",
            "full_name": "Login User",
        },
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "mypassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "wrong@example.com",
            "password": "correct",
            "full_name": "User",
        },
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "wrong@example.com", "password": "incorrect"},
    )
    assert response.status_code == 401


def test_get_profile_with_token(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "profile@example.com",
            "password": "pass123",
            "full_name": "Profile User",
        },
    )
    login = client.post(
        "/api/auth/login",
        json={"email": "profile@example.com", "password": "pass123"},
    )
    token = login.json()["access_token"]

    response = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "profile@example.com"


def test_get_profile_without_token(client):
    response = client.get("/api/users/me")
    assert response.status_code == 401
