

import pytest
from unittest.mock import patch, MagicMock
from services.truck_service import (
    create_truck,
    edit_truck,
    delete_truck,
    list_trucks,
    get_truck_by_id
)

@pytest.fixture
def mock_session():
    mock = MagicMock()
    with patch("services.truck_service.get_session", return_value=mock):
        yield mock

# 🚚 CREATE TRUCK
@patch("services.truck_service.get_session")

def test_create_truck_success(mock_session):
    mock_s = mock_session.return_value
    mock_s.query().filter_by().first.return_value = None  # No existe el camión

    mock_truck = MagicMock()
    mock_truck.camion_id = 1
    mock_truck.placa = "ABC123"
    mock_truck.capacidad = 10000
    mock_truck.tipo = "tipo"
    mock_truck.fecha_registro = None
    mock_truck.rutas = "Ruta 1"

    mock_s.refresh.return_value = None
    mock_s.add.return_value = None

    with patch("services.truck_service.Truck", return_value=mock_truck):
        response, status = create_truck({
            "placa": "ABC123",
            "capacidad": 10000,
            "tipo": "tipo",
            "rutas": "Ruta 1"
        })

    assert status == 201
    assert response["message"] == "Camión registrado"

@patch("services.truck_service.get_session")

def test_create_truck_duplicate(mock_session):
    mock_s = mock_session.return_value
    mock_s.query().filter_by().first.return_value = MagicMock()  # Camión ya existe

    response, status = create_truck({
        "placa": "ABC123",
        "capacidad": 10000
    })

    assert status == 409
    assert "error" in response

# ✏️ EDIT TRUCK
@patch("services.truck_service.get_session")
def test_edit_truck_success(mock_session):
    mock_s = mock_session.return_value

    # Mock para el camión que se va a editar
    mock_truck = MagicMock()
    mock_truck.placa = "DEF456"
    mock_truck.capacidad = 10000
    mock_truck.tipo = "tipo"
    mock_truck.rutas = "Ruta A"
    mock_truck.fecha_registro = None

    # Simula el flujo correcto:
    # 1. Encuentra el camión a editar (mock_truck)
    # 2. No encuentra duplicado (None)
    mock_s.query().filter.return_value.first.side_effect = [mock_truck, None]

    data = {"placa": "XYZ789", "capacidad": 15000}
    response, status = edit_truck(data, 1)

    assert status == 200
    assert response["message"] == "Camión actualizado"


@patch("services.truck_service.get_session")

def test_edit_truck_not_found(mock_session):
    mock_s = mock_session.return_value
    mock_s.query().filter.return_value.first.return_value = None

    response, status = edit_truck({"placa": "XYZ789"}, 99)

    assert status == 404
    assert "error" in response

@patch("services.truck_service.get_session")

def test_edit_truck_duplicate_plate(mock_session):
    mock_s = mock_session.return_value

    existing_truck = MagicMock()
    truck_to_edit = MagicMock()
    truck_to_edit.placa = "OLD123"

    # Simula encontrar el camión a editar
    mock_s.query().filter.return_value.first.side_effect = [truck_to_edit, existing_truck]

    data = {"placa": "DUPLICATE123"}

    response, status = edit_truck(data, 1)

    assert status == 409
    assert "error" in response

# 🗑️ DELETE TRUCK
@patch("services.truck_service.get_session")

def test_delete_truck_success(mock_session):
    mock_s = mock_session.return_value
    mock_truck = MagicMock()

    mock_s.query().filter.return_value.first.return_value = mock_truck

    response, status = delete_truck(1)

    assert status == 200
    assert response["message"] == "Camión eliminado exitosamente"

@patch("services.truck_service.get_session")

def test_delete_truck_not_found(mock_session):
    mock_s = mock_session.return_value
    mock_s.query().filter.return_value.first.return_value = None

    response, status = delete_truck(999)

    assert status == 404
    assert "error" in response

# 📄 LIST TRUCKS
@patch("services.truck_service.get_session")

def test_list_trucks_success(mock_session):
    mock_s = mock_session.return_value
    mock_truck = MagicMock()
    mock_truck.camion_id = 1
    mock_truck.placa = "AAA111"
    mock_truck.capacidad = 5000
    mock_truck.tipo = "tipo"
    mock_truck.fecha_registro = None
    mock_truck.rutas = "Ruta X"

    mock_s.query().all.return_value = [mock_truck]

    response, status = list_trucks()

    assert status == 200
    assert isinstance(response["camiones"], list)
    assert response["camiones"][0]["placa"] == "AAA111"

@patch("services.truck_service.get_session")

def test_list_trucks_error(mock_session):
    mock_s = mock_session.return_value
    mock_s.query().all.side_effect = Exception("error inesperado")

    response, status = list_trucks()

    assert status == 500
    assert "error" in response

# 🔍 GET TRUCK BY ID
@patch("services.truck_service.get_session")

def test_get_truck_by_id_success(mock_session):
    mock_s = mock_session.return_value
    mock_truck = MagicMock()
    mock_truck.camion_id = 1
    mock_truck.placa = "ZZZ999"
    mock_truck.capacidad = 7500
    mock_truck.tipo = "tipo"
    mock_truck.fecha_registro = None
    mock_truck.rutas = "Ruta Final"

    mock_s.query().filter.return_value.first.return_value = mock_truck

    response, status = get_truck_by_id(1)

    assert status == 200
    assert response["placa"] == "ZZZ999"

@patch("services.truck_service.get_session")
def test_get_truck_by_id_not_found(mock_session):
    mock_s = mock_session.return_value
    mock_s.query().filter.return_value.first.return_value = None

    response, status = get_truck_by_id(12345)

    assert status == 404
    assert "error" in response
