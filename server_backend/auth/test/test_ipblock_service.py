import pytest
from unittest.mock import patch, MagicMock
from services.ipblock_service import is_ip_blocked, register_failed_attempt, reset_ip

IP = "192.168.1.100"

@pytest.fixture
def mock_redis():
    mock = MagicMock()
    with patch("services.ipblock_service.get_redis_client", return_value=mock):
        yield mock

# ✅ Test: IP bloqueada (umbral alcanzado)
def test_is_ip_blocked_true(mock_redis):
    mock_redis.get.return_value = b'5'  # igual al umbral
    assert is_ip_blocked(IP) is True
    mock_redis.get.assert_called_with(f"ipblock:{IP}")

# ✅ Test: IP no bloqueada
def test_is_ip_blocked_false(mock_redis):
    mock_redis.get.return_value = b'2'
    assert is_ip_blocked(IP) is False

# ✅ Test: registro de intento fallido cuando ya hay valor
def test_register_failed_attempt_incr(mock_redis):
    mock_redis.get.return_value = b'3'
    register_failed_attempt(IP)
    mock_redis.incr.assert_called_once_with(f"ipblock:{IP}")

# ✅ Test: registro de intento fallido cuando es el primer intento
def test_register_failed_attempt_setex(mock_redis):
    mock_redis.get.return_value = None
    register_failed_attempt(IP)
    mock_redis.setex.assert_called_once_with(f"ipblock:{IP}", 15 * 60, 1)

# ✅ Test: resetear IP (eliminar la clave)
def test_reset_ip(mock_redis):
    reset_ip(IP)
    mock_redis.delete.assert_called_once_with(f"ipblock:{IP}")
