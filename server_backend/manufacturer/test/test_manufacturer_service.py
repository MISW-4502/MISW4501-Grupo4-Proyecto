import pytest
from unittest.mock import patch, MagicMock
from services.manufacturer_service import (
    create_manufacturer, edit_manufacturer, delete_manufacturer,
    list_manufacturers, get_manufacturer_by_id
)

@pytest.fixture
def mock_session():
    mock = MagicMock()
    with patch("services.manufacturer_service.get_session", return_value=mock):
        yield mock

# ✅ Crear fabricante exitosamente
def test_create_manufacturer_success(mock_session):
    mock_manufacturer = MagicMock()
    mock_manufacturer.fabricante_id = 1
    mock_manufacturer.nombre = "FabricanteX"
    mock_manufacturer.pais_origen = "Colombia"
    mock_manufacturer.categoria = "Electrónica"
    mock_manufacturer.creado_en = None

    mock_session.refresh.side_effect = lambda m: None

    with patch("services.manufacturer_service.Manufacturer", return_value=mock_manufacturer):
        data = {
            "nombre": "FabricanteX",
            "pais_origen": "Colombia",
            "categoria": "Electrónica"
        }
        response, code = create_manufacturer(data)
        assert code == 201
        assert response["fabricante"]["nombre"] == "FabricanteX"

# ✅ Editar fabricante exitosamente
def test_edit_manufacturer_success(mock_session):
    manufacturer = MagicMock()
    manufacturer.fabricante_id = 1
    manufacturer.nombre = "Old Name"
    manufacturer.pais_origen = "México"
    manufacturer.categoria = "Automotriz"
    manufacturer.creado_en = None

    mock_session.query().filter_by().first.return_value = manufacturer
    updated_data = {"nombre": "Nuevo Nombre"}
    response, code = edit_manufacturer(updated_data, 1)
    assert code == 200
    assert response["fabricante"]["nombre"] == "Nuevo Nombre"

# ❌ Editar fabricante no existente
def test_edit_manufacturer_not_found(mock_session):
    mock_session.query().filter_by().first.return_value = None
    response, code = edit_manufacturer({"nombre": "X"}, 999)
    assert code == 404
    assert "no encontrado" in response["error"]

# ✅ Eliminar fabricante exitosamente
def test_delete_manufacturer_success(mock_session):
    manufacturer = MagicMock()
    mock_session.query().filter_by().first.return_value = manufacturer
    response, code = delete_manufacturer(1)
    assert code == 200
    assert response["message"] == "Fabricante eliminado"

# ❌ Eliminar fabricante no existente
def test_delete_manufacturer_not_found(mock_session):
    mock_session.query().filter_by().first.return_value = None
    response, code = delete_manufacturer(999)
    assert code == 404
    assert "no encontrado" in response["error"]

# ✅ Listar fabricantes
def test_list_manufacturers(mock_session):
    m = MagicMock()
    m.fabricante_id = 1
    m.nombre = "FabX"
    m.pais_origen = "España"
    m.categoria = "Ropa"
    m.creado_en = None

    mock_session.query().all.return_value = [m]
    response, code = list_manufacturers()
    assert code == 200
    assert isinstance(response["fabricantes"], list)
    assert response["fabricantes"][0]["nombre"] == "FabX"

# ✅ Obtener fabricante por ID existente
def test_get_manufacturer_by_id_success(mock_session):
    m = MagicMock()
    m.fabricante_id = 1
    m.nombre = "FabID"
    m.pais_origen = "Chile"
    m.categoria = "Alimentos"
    m.creado_en = None

    mock_session.query().filter_by().first.return_value = m
    response, code = get_manufacturer_by_id(1)
    assert code == 200
    assert response["nombre"] == "FabID"

# ❌ Obtener fabricante por ID no existente
def test_get_manufacturer_by_id_not_found(mock_session):
    mock_session.query().filter_by().first.return_value = None
    response, code = get_manufacturer_by_id(99)
    assert code == 404
    assert "no encontrado" in response["error"]
