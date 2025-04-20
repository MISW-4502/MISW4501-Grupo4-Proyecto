import json
from unittest.mock import patch, MagicMock
from src.services.producer import publish_to_queue


@patch("src.services.producer.pika.BlockingConnection")
def test_publish_to_queue_success(mock_blocking_connection):
    mock_channel = MagicMock()
    mock_connection = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_blocking_connection.return_value = mock_connection

    fake_products = [
        {"nombre": "Producto A", "precio_unitario": 10000, "cantidad": 5},
        {"nombre": "Producto B", "precio_unitario": 5000, "cantidad": 3},
    ]

    publish_to_queue(fake_products)

    # ✅ Verifica que se declaró la cola
    mock_channel.queue_declare.assert_called_once_with(queue="product_queue", durable=True)

    # ✅ Verifica que se publicó un mensaje por producto
    assert mock_channel.basic_publish.call_count == len(fake_products)

    # ✅ Verifica contenido de los mensajes enviados
    for i, call in enumerate(mock_channel.basic_publish.call_args_list):
        args, kwargs = call
        body = kwargs.get("body") or args[2]
        assert json.loads(body) == fake_products[i]

    # ✅ Verifica que se cerró la conexión
    mock_connection.close.assert_called_once()
