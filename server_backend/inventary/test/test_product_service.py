import pytest
import io
import pandas as pd
from unittest.mock import patch
from services.product_service import process_excel_and_save

# ✅ Test: archivo CSV válido
def test_process_valid_csv():
    csv_content = (
        "nombre,precio_unitario,cantidad,descripcion,tipo,ubicacion\n"
        "Producto1,10.5,100,Desc1,Tipo1,Ubicacion1"
    )
    file = type("FileMock", (), {"filename": "test.csv", "read": lambda self: csv_content.encode()})()
    file = io.BytesIO(file.read())  # Simula archivo subido
    file.filename = "test.csv"

    with patch("services.product_service.pd.read_csv", return_value=pd.read_csv(io.StringIO(csv_content))), \
         patch("services.product_service.publish_to_queue"):
        result = process_excel_and_save(file)
        assert result["enviados_a_cola"] == 1
        assert result["errores"] == []

# ✅ Test: archivo con columnas faltantes
def test_process_excel_missing_columns():
    df = pd.DataFrame({"nombre": ["Producto1"], "precio_unitario": [10.0]})  # faltan columnas
    file = type("FileMock", (), {"filename": "file.xlsx", "read": lambda self: b""})()
    file.filename = "file.xlsx"

    with patch("services.product_service.pd.read_excel", return_value=df):
        result = process_excel_and_save(file)
        assert "error" in result
        assert "Faltan columnas requeridas" in result["error"]

# ✅ Test: archivo con extensión inválida
def test_process_invalid_extension():
    file = type("FileMock", (), {"filename": "data.txt", "read": lambda self: b""})()
    file.filename = "data.txt"

    result = process_excel_and_save(file)
    assert "error" in result
    assert "Formato de archivo no soportado" in result["error"]
