import os
import json
import time
import datetime
import threading
import pika
import psycopg2
import psycopg2.extras
from psycopg2 import pool
from flask import Flask, Response, jsonify
from concurrent.futures import ThreadPoolExecutor
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(fmt="%(asctime)s %(levelname)s %(message)s")
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logHandler)

app = Flask(__name__)
NUM_THREADS = 15
executor = ThreadPoolExecutor(max_workers=NUM_THREADS)

DB_POOL = pool.SimpleConnectionPool(
    minconn=10, 
    maxconn=NUM_THREADS * 2,  
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

def get_db_connection():
    """Obtiene una conexión del pool."""
    return DB_POOL.getconn()

def release_db_connection(conn):
    """Devuelve la conexión al pool."""
    DB_POOL.putconn(conn)


@app.route("/inventary/ping", methods=["GET"])
def health_check():
    return 'pong', 200

def save_to_db(records):
    if isinstance(records, dict):
        records = [records]

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = """
        INSERT INTO producto (nombre, descripcion, precio_unitario, tipo, cantidad, ubicacion, creado_en)
        VALUES %s
        """

        values = [
            (
                rec["nombre"],
                rec.get("descripcion"),
                rec.get("precio_unitario"),
                rec.get("tipo"),
                rec.get("cantidad", 0),
                rec.get("ubicacion"),
                datetime.datetime.utcnow()
            )
            for rec in records
        ]

        psycopg2.extras.execute_values(cur, query, values, page_size=1000)
        conn.commit()
        logger.info({"message": f"✅ Insertados {len(values)} productos en la base de datos."})

    except Exception as e:
        conn.rollback()
        logger.error({"message": f"❌ Error al guardar en BD: {e}"})
    finally:
        cur.close()
        release_db_connection(conn)

def process_message(body):

    try:
        records = json.loads(body)
        logger.info({"message": f"📥 Procesando {len(records) if isinstance(records, list) else 1} registros en un hilo..."})
        
        save_to_db(records)

    except Exception as e:
        logger.error({"message": f"❌ Error procesando mensaje: {e}"})

def callback(ch, method, properties, body):
    executor.submit(process_message, body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def consume():
    while True:
        try:
            logger.info({"message": "🔄 Conectando a RabbitMQ..."})

            rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
            rabbitmq_user = os.getenv('RABBITMQ_USER', 'admin')
            rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'admin')
            queue_name = os.getenv('QUEUE_NAME', 'product_queue')

            credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)

            connection_params = pika.ConnectionParameters(
                host=rabbitmq_host,
                port=5672,
                credentials=credentials,
                heartbeat=600
            )

            connection = pika.BlockingConnection(connection_params)
            channel = connection.channel()
            channel.queue_declare(queue=queue_name, durable=True)

            channel.basic_qos(prefetch_count=NUM_THREADS * 5)
            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)

            logger.info({"message": "✅ Consumidor listo, esperando mensajes..."})
            channel.start_consuming()

        except (pika.exceptions.AMQPConnectionError, pika.exceptions.ChannelClosedByBroker) as e:
            logger.error({"message": f"⚠️ Conexión fallida: {str(e)}. Reintentando en 5 segundos..."})
            time.sleep(5)

def start_flask():
    app.run(host="0.0.0.0", port=3401)

if __name__ == "__main__": 
    threading.Thread(target=start_flask, daemon=True).start()
    consume()