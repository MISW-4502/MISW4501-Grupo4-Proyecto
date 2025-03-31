import pika
import json
import os
from src.config.config import Config


def publish_login_event(event):

    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    rabbitmq_user = os.getenv('RABBITMQ_USER', 'admin')
    rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'admin')
    queue_name = os.getenv('QUEUE_NAME', 'login_queue')
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection_params = pika.ConnectionParameters(
        host=rabbitmq_host,
        port=5672,
        credentials=credentials
    )

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key= queue_name,
        body=json.dumps(event),
        properties=pika.BasicProperties(delivery_mode=2)  # persistente
    )
    print("✅ Mensajes publicados con éxito.")
    connection.close()
