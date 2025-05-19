# image_ingest_service/app.py
from flask import Flask, request, jsonify
import base64
import pika
import os
import threading
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

# Flask para health check
app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def health_check():
    return 'pong', 200

@app.route("/frames", methods=["POST"])
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

def start_flask():
    app.run(host="0.0.0.0", port=3600)

if __name__ == "__main__":
    threading.Thread(target=start_flask, daemon=True).start()
    # No necesita consumir, solo publicar
    while True:
        pass  # mantener el proceso vivo
