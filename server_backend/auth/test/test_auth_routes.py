import pytest
from unittest.mock import patch
from main import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_ping(client):
    response = client.get('/auth/ping')
    assert response.status_code == 200
    assert response.json == {"status": "oks"}

@patch("src.services.auth_service.login_user")
def test_login_success(mock_login_user, client):
    mock_login_user.return_value = ({"token": "fake-token"}, 200)
    response = client.post('/auth/login', json={"username": "test@example.com", "password": "1234"})
    assert response.status_code == 200
    assert "token" in response.json

def test_login_missing_fields(client):
    response = client.post('/auth/login', json={})
    assert response.status_code == 400

@patch("src.services.auth_service.register_user")
def test_register_success(mock_register_user, client):
    mock_register_user.return_value = ({"message": "Usuario registrado", "token": "123"}, 201)
    response = client.post('/auth/register', json={
        "email": "test@example.com",
        "nombre": "Test User",
        "password": "1234"
    })
    assert response.status_code == 201
    assert "message" in response.json

def test_register_missing_fields(client):
    response = client.post('/auth/register', json={"email": "test@example.com"})
    assert response.status_code == 400

@patch("src.services.auth_service.initiate_password_reset")
def test_recover_success(mock_recover, client):
    mock_recover.return_value = ({"message": "Correo de recuperación enviado", "token": "abc"}, 200)
    response = client.post('/auth/recover', json={"username": "test@example.com"})
    assert response.status_code == 200
    assert "token" in response.json

def test_recover_missing_username(client):
    response = client.post('/auth/recover', json={})
    assert response.status_code == 400

@patch("src.services.auth_service.reset_password_by_token")
def test_reset_password_success(mock_reset, client):
    mock_reset.return_value = ({"message": "Contraseña actualizada con éxito"}, 200)
    response = client.post('/auth/reset-password?token=abc', json={"new_password": "nueva123"})
    assert response.status_code == 200
    assert "message" in response.json

def test_reset_password_missing_fields(client):
    response = client.post('/auth/reset-password')  # no token ni body
    assert response.status_code == 400
