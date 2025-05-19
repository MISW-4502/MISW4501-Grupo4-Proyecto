import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.services.sales_service import (
    getOrders,
    getOrderById,
    editOrder,
    editOrAddItemsOrder,
    eliminateItemOrder,
    eliminatedOrder,
    getOrdersByClientId,
    getOrdersBySellerId
)

FAKE_TOKEN = "fake_token"

class FakeDetalle:
    id_pedido = 1
    id_producto = 1
    cantidad = 2
    precio_unitario = 10000
    subtotal = Decimal("20000")

class FakePedido:
    pedido_id = 1
    id_cliente = 1
    id_vendedor = 2
    fecha_creacion = datetime(2024, 4, 20, 12, 0, 0)
    estado = "PENDIENTE"
    total = Decimal("20000")
    detalles = [FakeDetalle()]

@pytest.fixture
def fake_pedido():
    return FakePedido()

@patch("src.services.sales_service.get_session")
def test_get_orders(mock_session, fake_pedido):
    mock_s = MagicMock()
    mock_s.query().all.return_value = [fake_pedido]
    mock_session.return_value = mock_s

    result = getOrders()
    assert isinstance(result, list)
    assert result[0]["pedido_id"] == 1

@patch("src.services.sales_service.get_session")
def test_eliminated_order_invalid_state(mock_session, fake_pedido):
    fake_pedido.estado = "ENVIADO"
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = fake_pedido
    mock_session.return_value = mock_s

    result, status = eliminatedOrder(1, token=FAKE_TOKEN)
    assert status == 400
    assert "estado" in result["error"]

@patch("src.services.sales_service.get_session")
def test_edit_order_success(mock_session, fake_pedido):
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = fake_pedido
    mock_session.return_value = mock_s

    data = {"estado": "ENVIADO", "id_vendedor": 99}
    result, status = editOrder(1, data)

    assert status == 200
    assert "actualizado" in result["message"]

@patch("src.services.sales_service.get_session")
def test_eliminate_item_success(mock_session, fake_pedido):
    class FakeDetalle:
        id_producto = 1
        pedido = fake_pedido
        subtotal = 10000
        cantidad = 2  # ✅ ¡Este es el que faltaba!

    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = FakeDetalle()
    mock_session.return_value = mock_s

    result, status = eliminateItemOrder(1, 1, token=FAKE_TOKEN)
    assert status == 200
    assert "eliminado" in result["message"]


def mock_first_effect():
    responses = [FakePedido(), FakeDetalle(), None]
    def _inner(*args, **kwargs):
        return responses.pop(0)
    return _inner

@patch("src.services.sales_service.get_session")
def test_edit_or_add_items_success(mock_session):
    mock_s = MagicMock()
    mock_s.query().filter_by().first.side_effect = mock_first_effect()
    mock_session.return_value = mock_s

    items = [
        {"id_producto": 1, "cantidad": 3, "precio_unitario": 12000},
        {"id_producto": 2, "cantidad": 1, "precio_unitario": 8000}
    ]

    result, status = editOrAddItemsOrder(1, items, token=FAKE_TOKEN)
    assert status in (200, 207)
    assert "actualizado" in result["message"]

@patch("src.services.sales_service.get_session")
def test_edit_or_add_items_no_pedido(mock_session):
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = None
    mock_session.return_value = mock_s

    result, status = editOrAddItemsOrder(999, [], token=FAKE_TOKEN)
    assert status == 404
    assert "error" in result

@patch("src.services.sales_service.get_session")
def test_edit_or_add_items_invalid_items(mock_session):
    pedido = FakePedido()
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = pedido
    mock_session.return_value = mock_s

    items = [{"id_producto": None, "cantidad": -1, "precio_unitario": 0}]
    result, status = editOrAddItemsOrder(1, items, token=FAKE_TOKEN)

    assert status == 207
    assert "errores" in result

@patch("src.services.sales_service.get_session")
def test_eliminate_item_not_found(mock_session):
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = None
    mock_session.return_value = mock_s

    result, status = eliminateItemOrder(1, 999, token=FAKE_TOKEN)
    assert status == 404
    assert "error" in result

@patch("src.services.sales_service.get_session")
def test_eliminate_item_invalid_state(mock_session):
    detalle = MagicMock()
    detalle.pedido.estado = "ENVIADO"
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = detalle
    mock_session.return_value = mock_s

    result, status = eliminateItemOrder(1, 1, token=FAKE_TOKEN)
    assert status == 400
    assert "error" in result

@patch("src.services.sales_service.get_session")
def test_eliminated_order_not_found(mock_session):
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = None
    mock_session.return_value = mock_s

    result, status = eliminatedOrder(999, token=FAKE_TOKEN)
    assert status == 404
    assert "error" in result

@patch("src.services.sales_service.get_session")
def test_get_orders_by_client_success(mock_session, fake_pedido):
    mock_s = MagicMock()
    mock_s.query().filter_by().all.return_value = [fake_pedido]
    mock_session.return_value = mock_s

    result = getOrdersByClientId(1)
    assert isinstance(result, list)
    assert result[0]["id_cliente"] == 1

@patch("src.services.sales_service.get_session")
def test_get_orders_by_client_empty(mock_session):
    mock_s = MagicMock()
    mock_s.query().filter_by().all.return_value = []
    mock_session.return_value = mock_s

    result = getOrdersByClientId(999)
    assert result == []

@patch("src.services.sales_service.get_session")
def test_get_orders_by_seller_success(mock_session, fake_pedido):
    mock_s = MagicMock()
    mock_s.query().filter_by().all.return_value = [fake_pedido]
    mock_session.return_value = mock_s

    result = getOrdersBySellerId(2)
    assert isinstance(result, list)
    assert result[0]["id_vendedor"] == 2

@patch("src.services.sales_service.get_session")
def test_get_orders_by_seller_empty(mock_session):
    mock_s = MagicMock()
    mock_s.query().filter_by().all.return_value = []
    mock_session.return_value = mock_s

    result = getOrdersBySellerId(999)
    assert result == []

@patch("src.services.sales_service.get_session")
@patch("src.services.sales_service.requests.get")
def test_get_order_by_id_with_token(mock_requests_get, mock_get_session, fake_pedido):
    mock_session = MagicMock()
    mock_session.query().filter_by().first.return_value = fake_pedido
    mock_get_session.return_value = mock_session

    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = [
        {"producto_id": 1, "nombre": "Producto Test"}
    ]

    token = FAKE_TOKEN
    result = getOrderById(1, token)

    assert result["pedido_id"] == 1
    assert result["detalles"][0]["nombre"] == "Producto Test"
    assert mock_requests_get.called
    assert "Authorization" in mock_requests_get.call_args[1]["headers"]
