# image_ingest_service/app.py
from flask import  request, jsonify
import base64
import pika
import os
import logging
from pythonjsonlogger import jsonlogger

# Logging con formato JSON
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(fmt="%(asctime)s %(levelname)s %(message)s")
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logHandler)

# Configuración
RABBITMQ_HOST = os.getenv("RABBITMQ_URL", "rabbitmq")
QUEUE_NAME = os.getenv("QUEUE_NAME", "frame_queue")


def receive_frame():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    try:
        content = file.read()
        encoded_image = base64.b64encode(content).decode("utf-8")

        # Conexión a RabbitMQ
        logger.info({"message": "📤 Conectando a RabbitMQ para publicar imagen..."})
        params = pika.URLParameters(RABBITMQ_HOST)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=encoded_image
        )

        connection.close()
        logger.info({"message": "✅ Imagen enviada correctamente al queue."})
        return jsonify({"message": "Frame enviado correctamente"}), 200

    except Exception as e:
        logger.error({"message": f"❌ Error publicando imagen: {str(e)}"})
        return jsonify({"error": str(e)}), 500
