import pika
import json
import os

def publish_order_to_queue(order):
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    rabbitmq_user = os.getenv('RABBITMQ_USER', 'admin')
    rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'admin')
    queue_name = os.getenv('QUEUE_NAME', 'order_queue')

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection_params = pika.ConnectionParameters(
        host=rabbitmq_host,
        port=5672,
        credentials=credentials
    )

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    # 🔥 Enviar un solo mensaje con el pedido completo
    message = json.dumps(order)

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )

    print("✅ Pedido publicado con éxito.")
    connection.close()
