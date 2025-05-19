import pytest
from unittest.mock import patch, MagicMock
from services.product_service import create_product, list_products, update_product, delete_product, r_stock, rel_stock

@pytest.fixture
def mock_session():
    mock = MagicMock()
    with patch("services.product_service.get_session", return_value=mock):
        yield mock

# ✅ Crear producto exitosamente
def test_create_product_success(mock_session):
    mock_add = MagicMock()
    mock_commit = MagicMock()
    mock_refresh = MagicMock()

    mock_session.add = mock_add
    mock_session.commit = mock_commit
    mock_session.refresh = mock_refresh

    data = {
        "nombre": "Producto Test",
        "precio_unitario": 19.99,
        "cantidad": 10,
        "descripcion": "Descripción",
        "tipo": "TipoA",
        "ubicacion": "Bodega"
    }

    result, error = create_product(data)
    assert error is None
    assert result["nombre"] == "Producto Test"

# ❌ Crear producto con campos obligatorios faltantes
def test_create_product_missing_fields(mock_session):
    data = {
        "precio_unitario": 15.0
    }
    result, error = create_product(data)
    assert result is None
    assert "obligatorios" in error

# ✅ Listar todos los productos
def test_list_products_all(mock_session):
    mock_product = MagicMock()
    mock_product.producto_id = 1
    mock_product.nombre = "P1"
    mock_product.precio_unitario = 10.0
    mock_product.cantidad = 5
    mock_product.descripcion = "D"
    mock_product.tipo = "T"
    mock_product.ubicacion = "U"
    mock_product.creado_en = None

    mock_session.query().all.return_value = [mock_product]

    result, error = list_products()
    assert isinstance(result, list)
    assert result[0]["nombre"] == "P1"
    assert error is None

# ✅ Actualizar producto exitosamente
def test_update_product_success(mock_session):
    mock_product = MagicMock()
    mock_product.producto_id = 1

    mock_session.query().get.return_value = mock_product

    updated_data = {"nombre": "Nuevo Nombre"}
    result, error = update_product(1, updated_data)
    assert error is None
    assert result["nombre"] == "Nuevo Nombre"

# ❌ Actualizar producto no existente
def test_update_product_not_found(mock_session):
    mock_session.query().get.return_value = None
    result, error = update_product(999, {"nombre": "X"})
    assert result is None
    assert "no encontrado" in error

# ✅ Eliminar producto exitosamente
def test_delete_product_success(mock_session):
    mock_product = MagicMock()
    mock_session.query().get.return_value = mock_product

    success, error = delete_product(1)
    assert success is True
    assert error is None

# ❌ Eliminar producto no existente
def test_delete_product_not_found(mock_session):
    mock_session.query().get.return_value = None

    success, error = delete_product(999)
    assert success is False
    assert "no encontrado" in error


# ✅ Obtener producto específico
def test_list_products_by_id(mock_session):
    mock_product = MagicMock()
    mock_product.producto_id = 5
    mock_product.nombre = "Unitario"
    mock_product.precio_unitario = 9.99
    mock_product.cantidad = 100
    mock_product.descripcion = "desc"
    mock_product.tipo = "tipo"
    mock_product.ubicacion = "ubic"
    mock_product.creado_en = None

    mock_session.query().get.return_value = mock_product

    result, error = list_products(product_id=5)
    assert result["producto_id"] == 5
    assert error is None

# ❌ Producto por ID no encontrado
def test_list_product_not_found(mock_session):
    mock_session.query().get.return_value = None
    result, error = list_products(product_id=99)
    assert result is None
    assert "no encontrado" in error

def test_r_stock_success(mock_session):
    mock_product = MagicMock()
    mock_product.cantidad = 10
    mock_session.query().get.return_value = mock_product

    success, error = r_stock(1, 3)
    assert success
    assert error is None
    assert mock_product.cantidad == 7

# ❌ Reservar stock insuficiente
def test_r_stock_insuficiente(mock_session):
    mock_product = MagicMock()
    mock_product.cantidad = 2
    mock_session.query().get.return_value = mock_product

    success, error = r_stock(1, 5)
    assert not success
    assert "insuficiente" in error

# ❌ Reservar stock - producto no existe
def test_r_stock_not_found(mock_session):
    mock_session.query().get.return_value = None
    success, error = r_stock(999, 1)
    assert not success
    assert "no encontrado" in error

# ✅ Liberar stock correctamente
def test_rel_stock_success(mock_session):
    mock_product = MagicMock()
    mock_product.cantidad = 5
    mock_session.query().get.return_value = mock_product

    success, error = rel_stock(1, 3)
    assert success
    assert error is None
    assert mock_product.cantidad == 8

# ❌ Liberar stock - producto no existe
def test_rel_stock_not_found(mock_session):
    mock_session.query().get.return_value = None
    success, error = rel_stock(999, 1)
    assert not success
    assert "no encontrado" in error