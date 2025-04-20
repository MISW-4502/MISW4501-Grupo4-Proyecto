# main.py

import os
import json
import time
import datetime
import threading
import pika
import psycopg2
import psycopg2.extras
from psycopg2 import pool
from flask import Flask
from concurrent.futures import ThreadPoolExecutor
import logging
from pythonjsonlogger import jsonlogger


logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(fmt="%(asctime)s %(levelname)s %(message)s")
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logHandler)

# Flask app para health check
app = Flask(__name__)
NUM_THREADS = 15
executor = ThreadPoolExecutor(max_workers=NUM_THREADS)

# Pool de conexiones a PostgreSQL
DB_POOL = pool.SimpleConnectionPool(
    minconn=10,
    maxconn=NUM_THREADS * 2,
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

def get_db_connection():
    return DB_POOL.getconn()

def release_db_connection(conn):
    DB_POOL.putconn(conn)

@app.route("/order/ping", methods=["GET"])
def health_check():
    return 'pong', 200

def save_order_to_db(data):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        total = 0
        # Insertar en tabla pedido
        logger.info({"data": data})
        logger.info({"detalles": data.get("detalles")})
        
        cur.execute("""
            INSERT INTO pedido (id_cliente, id_vendedor, fecha_creacion, estado, total)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING pedido_id
        """, (
            data['id_cliente'],
            data.get('id_vendedor'),
            datetime.datetime.utcnow(),
            'PENDIENTE',
            0
        ))

        pedido_id = cur.fetchone()[0]
        logger.info({"message": f"📝 Pedido creado con ID {pedido_id}"})

        # Insertar los detalles
        detalles = data['detalles']
        values = []
        for item in detalles:
            subtotal = item['cantidad'] * item['precio_unitario']
            total += subtotal
            values.append((
                pedido_id,
                item['id_producto'],
                item['cantidad'],
                item['precio_unitario'],
                subtotal
            ))

        psycopg2.extras.execute_values(cur, """
            INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
            VALUES %s
        """, values)

        # Actualizar total en pedido
        cur.execute("UPDATE pedido SET total = %s WHERE pedido_id = %s", (total, pedido_id))

        conn.commit()
        logger.info({"message": f"✅ Pedido {pedido_id} y {len(detalles)} detalles guardados. Total: {total}"})

    except Exception as e:
        conn.rollback()
        logger.error({"message": f"❌ Error al guardar pedido: {e}"})
    finally:
        cur.close()
        release_db_connection(conn)

def process_message(body):
    try:
        data = json.loads(body)
        logger.info({"message": "📥 Procesando pedido en hilo..."})
        save_order_to_db(data)
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
            queue_name = os.getenv('QUEUE_NAME', 'order_queue')

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

            logger.info({"message": "✅ Consumidor listo, esperando pedidos..."})
            channel.start_consuming()

        except (pika.exceptions.AMQPConnectionError, pika.exceptions.ChannelClosedByBroker) as e:
            logger.error({"message": f"⚠️ Conexión fallida: {str(e)}. Reintentando en 5 segundos..."})
            time.sleep(5)

def start_flask():
    app.run(host="0.0.0.0", port=3501)

if __name__ == "__main__":
    threading.Thread(target=start_flask, daemon=True).start()
    consume()
