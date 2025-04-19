from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, MagicMock
from services.auth_service import login_user, register_user, initiate_password_reset, reset_password_by_token



@pytest.fixture
def mock_session():
    mock = MagicMock()
    with patch("services.auth_service.get_session", return_value=mock):
        yield mock

# 🔐 LOGIN
def test_login_success(mock_session):
    mock_user = MagicMock()
    mock_user.password = "$2b$12$salteadofalso..."
    mock_session.query().filter_by().first.return_value = mock_user

    with patch("services.auth_service.check_password", return_value=True), \
         patch("services.auth_service.is_ip_blocked", return_value=False), \
         patch("services.auth_service.reset_ip"), \
         patch("services.auth_service.generate_token", return_value="token123"):

        data, status = login_user("user@test.com", "pass", "127.0.0.1")
        assert status == 200
        assert data["token"] == "token123"

# 🧾 REGISTRO
def test_register_user_existing_email(mock_session):
    mock_session.query().filter_by().first.return_value = True

    with patch("services.auth_service.is_ip_blocked", return_value=False):
        response, status = register_user("user@test.com", "Nombre", "ROL", "pass", "127.0.0.1")
        assert status == 409
        assert response["error"] == "El email ya está registrado"

# 📩 RECUPERACIÓN DE CONTRASEÑA
def test_initiate_password_reset_success(mock_session):
    mock_user = MagicMock()
    mock_session.query().filter_by().first.return_value = mock_user

    with patch("services.auth_service.is_ip_blocked", return_value=False), \
         patch("services.auth_service.uuid.uuid4", return_value="fake-uuid"):

        response, status = initiate_password_reset("user@test.com", "127.0.0.1")
        assert status == 200
        assert "token" in response
        assert response["token"] == "fake-uuid"

# 🔁 RESET DE CONTRASEÑA
def test_reset_password_by_token_success(mock_session):
    mock_reset = MagicMock()
    mock_reset.email = "user@test.com"
    mock_reset.expires_at = datetime.utcnow() + timedelta(minutes=30)  # ✅ Aquí está el cambio
    
    mock_user = MagicMock()

    mock_session.query().filter_by().first.side_effect = [mock_reset, mock_user]

    with patch("services.auth_service.hash_password", return_value="hashed123"):
        response, status = reset_password_by_token("valid-token", "newpassword")
        assert status == 200
        assert response["message"] == "Contraseña actualizada con éxito"
