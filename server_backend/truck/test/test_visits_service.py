import pytest
import datetime
from unittest.mock import patch, MagicMock
from src.services.visit_service import (
    create_visit,
    get_visit_by_id,
    list_visits,
    update_visit,
    delete_visit,
    list_visits_by_seller
)

@pytest.fixture
def mock_session():
    mock = MagicMock()
    with patch("src.services.visit_service.get_session", return_value=mock):
        yield mock

# 🆕 CREATE VISIT
@patch("src.services.visit_service.get_session")
def test_create_visit_success(mock_session):
    mock_s = mock_session.return_value
    mock_visit = MagicMock()
    mock_visit.visita_id = 1

    with patch("src.models.visita_model.Visita", return_value=mock_visit):
        data = {
            "id_vendedor": 1,
            "id_cliente": 2,
            "fecha_visita": "2025-05-01T10:00:00",
            "estado": "PENDIENTE",
            "descripcion": "Reunión inicial",
            "direccion": "Calle 123"
        }
        response, status = create_visit(data)

    assert status == 201
    assert response["message"] == "Visita creada exitosamente"

# 🔍 GET VISIT BY ID
@patch("src.services.visit_service.get_session")
def test_get_visit_by_id_success(mock_session):
    mock_s = mock_session.return_value
    mock_visit = MagicMock()
    mock_visit.visita_id = 1
    mock_visit.id_vendedor = 1
    mock_visit.id_cliente = 2
    mock_visit.fecha_visita = datetime.datetime(2025, 5, 1, 10, 0, 0)
    mock_visit.estado = "PENDIENTE"
    mock_visit.descripcion = "Reunión inicial"
    mock_visit.direccion = "Calle 123"

    mock_s.query().filter_by().first.return_value = mock_visit

    response, status = get_visit_by_id(1)

    assert status == 200
    assert response["visita_id"] == 1

@patch("src.services.visit_service.get_session")
def test_get_visit_by_id_not_found(mock_session):
    mock_s = mock_session.return_value
    mock_s.query().filter_by().first.return_value = None

    response, status = get_visit_by_id(999)

    assert status == 404
    assert "error" in response

# 📋 LIST VISITS
@patch("src.services.visit_service.get_session")
def test_list_visits_success(mock_session):
    mock_s = mock_session.return_value
    mock_visit = MagicMock()
    mock_visit.visita_id = 1
    mock_visit.id_vendedor = 1
    mock_visit.id_cliente = 2
    mock_visit.fecha_visita = datetime.datetime(2025, 5, 1, 10, 0, 0)
    mock_visit.estado = "PENDIENTE"
    mock_visit.descripcion = "Visita agendada"
    mock_visit.direccion = "Calle 123"

    mock_s.query().all.return_value = [mock_visit]

    response, status = list_visits()

    assert status == 200
    assert isinstance(response, list)
    assert response[0]["visita_id"] == 1

# ✏️ UPDATE VISIT
@patch("src.services.visit_service.get_session")
def test_update_visit_success(mock_session):
    mock_s = mock_session.return_value
    mock_visit = MagicMock()

    mock_s.query().filter_by().first.return_value = mock_visit

    data = {"estado": "COMPLETADA"}
    response, status = update_visit(1, data)

    assert status == 200
    assert response["message"] == "Visita actualizada exitosamente"

@patch("src.services.visit_service.get_session")
def test_update_visit_not_found(mock_session):
    mock_s = mock_session.return_value
    mock_s.query().filter_by().first.return_value = None

    response, status = update_visit(999, {"estado": "COMPLETADA"})

    assert status == 404
    assert "error" in response

# 🗑️ DELETE VISIT
@patch("src.services.visit_service.get_session")
def test_delete_visit_success(mock_session):
    mock_s = mock_session.return_value
    mock_visit = MagicMock()

    mock_s.query().filter_by().first.return_value = mock_visit

    response, status = delete_visit(1)

    assert status == 200
    assert response["message"] == "Visita eliminada exitosamente"

@patch("src.services.visit_service.get_session")
def test_delete_visit_not_found(mock_session):
    mock_s = mock_session.return_value
    mock_s.query().filter_by().first.return_value = None

    response, status = delete_visit(999)

    assert status == 404
    assert "error" in response

# 📄 LIST VISITS BY SELLER
@patch("src.services.visit_service.get_session")
def test_list_visits_by_seller_success(mock_session):
    mock_s = mock_session.return_value
    mock_visit = MagicMock()
    mock_visit.visita_id = 1
    mock_visit.id_cliente = 2
    mock_visit.fecha_visita = datetime.datetime(2025, 5, 1, 10, 0, 0)
    mock_visit.estado = "PENDIENTE"
    mock_visit.descripcion = "Visita de prueba"
    mock_visit.direccion = "Calle X"

    mock_s.query().filter().all.return_value = [mock_visit]

    response, status = list_visits_by_seller(1)

    assert status == 200
    assert isinstance(response, list)
    assert response[0]["visita_id"] == 1

@patch("src.services.visit_service.get_session")
def test_list_visits_by_seller_not_found(mock_session):
    mock_s = mock_session.return_value
    mock_s.query().filter().all.return_value = []

    response, status = list_visits_by_seller(1)

    assert status == 404
    assert "message" in response
