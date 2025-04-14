import pytest
from unittest.mock import patch, MagicMock
from services.product_service import create_product, list_products, update_product, delete_product

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
