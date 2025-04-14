import pytest
from unittest.mock import patch, MagicMock
from services.truck_service import create_truck, edit_truck, delete_truck, list_trucks, get_truck_by_id

@pytest.fixture
def mock_session():
    mock = MagicMock()
    with patch("services.truck_service.get_session", return_value=mock):
        yield mock

# ✅ Crear camión nuevo
def test_create_truck_success(mock_session):
    mock_session.query().filter_by().first.return_value = None  # No existe
    mock_truck = MagicMock()
    mock_truck.camion_id = 1
    mock_truck.placa = "ABC123"
    mock_truck.capacidad = 20
    mock_truck.tipo = "Tipo A"
    mock_truck.fecha_registro = None
    mock_truck.rutas = "Ruta X"

    mock_session.refresh.side_effect = lambda x: x

    with patch("services.truck_service.Truck", return_value=mock_truck):
        result, code = create_truck({
            "placa": "ABC123",
            "capacidad": 20,
            "tipo": "Tipo A",
            "rutas": "Ruta X"
        })
        assert code == 201
        assert result["camion"]["placa"] == "ABC123"

# ❌ Crear camión duplicado
def test_create_truck_duplicate(mock_session):
    mock_session.query().filter_by().first.return_value = True
    result, code = create_truck({
        "placa": "ABC123",
        "capacidad": 20
    })
    assert code == 409
    assert "Ya existe un camión" in result["error"]

# ✅ Editar camión exitosamente

def test_edit_truck_success(mock_session):
    truck = MagicMock()
    truck.camion_id = 1
    truck.placa = "ABC123"
    truck.capacidad = 10
    truck.tipo = "tipo"
    truck.fecha_registro = None
    truck.rutas = "Ruta1"

    # 👉 Primer filter() es el truck a editar, segundo filter() verifica si ya existe otra placa (debe ser None)
    mock_session.query().filter().first.side_effect = [truck, None]

    result, code = edit_truck({
        "placa": "DEF456",
        "capacidad": 30
    }, 1)

    assert code == 200
    assert result["camion"]["placa"] == "DEF456"



# ❌ Eliminar camión no existente
def test_delete_truck_not_found(mock_session):
    mock_session.query().filter().first.return_value = None
    result, code = delete_truck(99)
    assert code == 404
    assert "no encontrado" in result["error"]

# ✅ Listar camiones
def test_list_trucks_success(mock_session):
    truck = MagicMock()
    truck.camion_id = 1
    truck.placa = "AAA111"
    truck.capacidad = 40
    truck.tipo = "Frigorífico"
    truck.fecha_registro = None
    truck.rutas = "Norte"

    mock_session.query().all.return_value = [truck]
    result, code = list_trucks()
    assert code == 200
    assert len(result["camiones"]) == 1

# ✅ Obtener camión por ID existente
def test_get_truck_by_id_success(mock_session):
    truck = MagicMock()
    truck.camion_id = 1
    truck.placa = "ZZZ999"
    truck.capacidad = 10
    truck.tipo = "Pequeño"
    truck.fecha_registro = None
    truck.rutas = "Sur"

    mock_session.query().filter().first.return_value = truck
    result, code = get_truck_by_id(1)
    assert code == 200
    assert result["placa"] == "ZZZ999"
