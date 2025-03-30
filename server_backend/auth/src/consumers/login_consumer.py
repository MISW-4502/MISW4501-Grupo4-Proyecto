import pika, os, time, json
import logging
from concurrent.futures import ThreadPoolExecutor
from pythonjsonlogger import jsonlogger
from src.services.auth_service import authenticate_user
from src.services.auth_service import authenticate_user, generate_token


# Config
NUM_THREADS = 5
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
rabbitmq_user = os.getenv('RABBITMQ_USER', 'admin')
rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'admin')
queue_name = os.getenv('QUEUE_NAME', 'login_queue')

# Logger setup
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(fmt="%(asctime)s %(levelname)s %(message)s")
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logHandler)

# Executor pool
executor = ThreadPoolExecutor(max_workers=NUM_THREADS)

def process_message(body):
    try:
        data = json.loads(body)
        username = data.get("username")
        password = data.get("password")

        logger.info({"message": f"📩 Mensaje recibido", "user": username})

        if authenticate_user(username, password):
            token = generate_token(username)
            logger.info({"message": f"✅ Usuario autenticado", "user": username, "token": token})
            # 🚨 En producción deberías enviar este token de vuelta (RabbitMQ, respuesta HTTP, etc.)
        else:
            logger.warning({"message": f"❌ Autenticación fallida", "user": username})

    except Exception as e:
        logger.error({"message": "🔥 Error procesando mensaje", "error": str(e)})

def callback(ch, method, properties, body):
    executor.submit(process_message, body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def consume():
    while True:
        try:
            logger.info({"message": "🔄 Conectando a RabbitMQ..."})

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

            logger.info({"message": f"✅ Consumidor listo en cola '{queue_name}' con {NUM_THREADS} hilos."})
            channel.start_consuming()

        except (pika.exceptions.AMQPConnectionError, pika.exceptions.ChannelClosedByBroker) as e:
            logger.error({"message": f"⚠️ Conexión fallida: {str(e)}. Reintentando en 5 segundos..."})
            time.sleep(5)
