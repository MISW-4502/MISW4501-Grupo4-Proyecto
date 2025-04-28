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


# 🔹 Test: getOrders devuelve estructura válida
@patch("src.services.sales_service.get_session")
def test_get_orders(mock_session, fake_pedido):
    mock_s = MagicMock()
    mock_s.query().all.return_value = [fake_pedido]
    mock_session.return_value = mock_s

    result = getOrders()
    assert isinstance(result, list)
    assert result[0]["pedido_id"] == 1

# 🔹 Test: getOrderById devuelve pedido con detalles
@patch("src.services.sales_service.get_session")
def test_get_order_by_id(mock_session, fake_pedido):
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = fake_pedido
    mock_session.return_value = mock_s

    result = getOrderById(1)
    assert result["pedido_id"] == 1
    assert len(result["detalles"]) == 1

# 🔹 Test: eliminar pedido sin estado PENDIENTE
@patch("src.services.sales_service.get_session")
def test_eliminated_order_invalid_state(mock_session, fake_pedido):
    fake_pedido.estado = "ENVIADO"
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = fake_pedido
    mock_session.return_value = mock_s

    result, status = eliminatedOrder(1)
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

    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = FakeDetalle()
    mock_session.return_value = mock_s

    result, status = eliminateItemOrder(1, 1)
    assert status == 200
    assert "eliminado" in result["message"]

def mock_first_effect():
    responses = [FakePedido(), FakeDetalle(), None]  # Pedido → Detalle1 → Detalle2 (no existe)
    def _inner(*args, **kwargs):
        return responses.pop(0)
    return _inner


@patch("src.services.sales_service.get_session")
def test_edit_or_add_items_success(mock_session):
    mock_s = MagicMock()
    mock_s.query().filter_by().first.side_effect = mock_first_effect()
    mock_session.return_value = mock_s

    items = [
        {"id_producto": 1, "cantidad": 3, "precio_unitario": 12000},  # Modificar
        {"id_producto": 2, "cantidad": 1, "precio_unitario": 8000}    # Agregar
    ]

    result, status = editOrAddItemsOrder(1, items)
    assert status in (200, 207)
    assert "actualizado" in result["message"]

@pytest.fixture
def fake_pedido():
    return FakePedido()


# 🔹 Test: getOrderById cuando no existe pedido
@patch("src.services.sales_service.get_session")
def test_get_order_by_id_not_found(mock_session):
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = None
    mock_session.return_value = mock_s

    result = getOrderById(999)
    assert result is None


# 🔹 Test: editOrder cuando no encuentra pedido
@patch("src.services.sales_service.get_session")
def test_edit_order_not_found(mock_session):
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = None
    mock_session.return_value = mock_s

    result, status = editOrder(999, {"estado": "ENVIADO"})
    assert status == 404
    assert "error" in result


# 🔹 Test: editOrAddItemsOrder cuando pedido no existe
@patch("src.services.sales_service.get_session")
def test_edit_or_add_items_no_pedido(mock_session):
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = None
    mock_session.return_value = mock_s

    result, status = editOrAddItemsOrder(999, [])
    assert status == 404
    assert "error" in result


# 🔹 Test: editOrAddItemsOrder errores en datos
@patch("src.services.sales_service.get_session")
def test_edit_or_add_items_invalid_items(mock_session):
    pedido = FakePedido()
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = pedido
    mock_session.return_value = mock_s

    items = [{"id_producto": None, "cantidad": -1, "precio_unitario": 0}]
    result, status = editOrAddItemsOrder(1, items)

    assert status == 207
    assert "errores" in result


# 🔹 Test: eliminateItemOrder cuando detalle no existe
@patch("src.services.sales_service.get_session")
def test_eliminate_item_not_found(mock_session):
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = None
    mock_session.return_value = mock_s

    result, status = eliminateItemOrder(1, 999)
    assert status == 404
    assert "error" in result


# 🔹 Test: eliminateItemOrder cuando estado no es PENDIENTE
@patch("src.services.sales_service.get_session")
def test_eliminate_item_invalid_state(mock_session):
    detalle = MagicMock()
    detalle.pedido.estado = "ENVIADO"
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = detalle
    mock_session.return_value = mock_s

    result, status = eliminateItemOrder(1, 1)
    assert status == 400
    assert "error" in result


# 🔹 Test: eliminatedOrder cuando pedido no existe
@patch("src.services.sales_service.get_session")
def test_eliminated_order_not_found(mock_session):
    mock_s = MagicMock()
    mock_s.query().filter_by().first.return_value = None
    mock_session.return_value = mock_s

    result, status = eliminatedOrder(999)
    assert status == 404
    assert "error" in result


# 🔹 Test: getOrdersByClientId - cliente con pedidos
@patch("src.services.sales_service.get_session")
def test_get_orders_by_client_success(mock_session, fake_pedido):
    mock_s = MagicMock()
    mock_s.query().filter_by().all.return_value = [fake_pedido]
    mock_session.return_value = mock_s

    result = getOrdersByClientId(1)
    assert isinstance(result, list)
    assert result[0]["id_cliente"] == 1


# 🔹 Test: getOrdersByClientId - cliente sin pedidos
@patch("src.services.sales_service.get_session")
def test_get_orders_by_client_empty(mock_session):
    mock_s = MagicMock()
    mock_s.query().filter_by().all.return_value = []
    mock_session.return_value = mock_s

    result = getOrdersByClientId(999)
    assert result == []


# 🔹 Test: getOrdersBySellerId - vendedor con pedidos
@patch("src.services.sales_service.get_session")
def test_get_orders_by_seller_success(mock_session, fake_pedido):
    mock_s = MagicMock()
    mock_s.query().filter_by().all.return_value = [fake_pedido]
    mock_session.return_value = mock_s

    result = getOrdersBySellerId(2)
    assert isinstance(result, list)
    assert result[0]["id_vendedor"] == 2


# 🔹 Test: getOrdersBySellerId - vendedor sin pedidos
@patch("src.services.sales_service.get_session")
def test_get_orders_by_seller_empty(mock_session):
    mock_s = MagicMock()
    mock_s.query().filter_by().all.return_value = []
    mock_session.return_value = mock_s

    result = getOrdersBySellerId(999)
    assert result == []
