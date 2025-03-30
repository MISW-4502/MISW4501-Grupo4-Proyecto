import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

def publish_login_event(event):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue='login_queue', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='login_queue',
        body=json.dumps(event),
        properties=pika.BasicProperties(delivery_mode=2)  # persistente
    )

    connection.close()
