import os
import base64
import pika
import cv2
import numpy as np
import logging
from pythonjsonlogger import jsonlogger

# Logger JSON
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(fmt="%(asctime)s %(levelname)s %(message)s")
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logHandler)

# Config
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin")
QUEUE_NAME = os.getenv("QUEUE_NAME", "frame_queue")

def process_image(encoded_image):
    try:
        # Decodificar base64
        img_bytes = base64.b64decode(encoded_image)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Procesamiento básico (convertir a escala de grises)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        logger.info({"message": "✅ Imagen procesada (convertida a gris)"})

        # Puedes guardar o enviar resultado, por ahora solo logueamos
    except Exception as e:
        logger.error({"message": f"❌ Error procesando imagen: {e}"})

def callback(ch, method, properties, body):
    logger.info({"message": "📥 Recibida imagen desde RabbitMQ"})
    process_image(body.decode())
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    logger.info({"message": "🔄 Conectando a RabbitMQ..."})
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        credentials=credentials
    ))

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    logger.info({"message": f"✅ Esperando imágenes en '{QUEUE_NAME}'..."})
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()
