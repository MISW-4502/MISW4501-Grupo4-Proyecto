import json
import pytest
from unittest.mock import patch, MagicMock
from src.services.sales_producer import publish_order_to_queue


@patch("src.services.sales_producer.pika.BlockingConnection")
def test_publish_order_to_queue_success(mock_blocking_connection):
    mock_channel = MagicMock()
    mock_connection = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_blocking_connection.return_value = mock_connection

    fake_order = {
        "id_cliente": 1,
        "id_vendedor": 2,
        "detalles": [
            {"id_producto": 10, "cantidad": 2, "precio_unitario": 5000}
        ]
    }

    publish_order_to_queue(fake_order)

    # ✅ Verifica conexión y publicación
    mock_channel.queue_declare.assert_called_once_with(queue="order_queue", durable=True)
    mock_channel.basic_publish.assert_called_once()

    # ✅ Verifica que el mensaje enviado es el esperado
    args, kwargs = mock_channel.basic_publish.call_args
    assert kwargs["routing_key"] == "order_queue"
    assert json.loads(kwargs["body"]) == fake_order

    # ✅ Verifica cierre de conexión
    mock_connection.close.assert_called_once()
