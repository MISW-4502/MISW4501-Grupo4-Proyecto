import os


class Config:
    
    RABBIT_CONFIG = {
    "host": os.getenv('RABBITMQ_HOST', 'rabbitmq-service-deploy'),
    "user": os.getenv('RABBITMQ_USER', 'admin'),
    "password": os.getenv('RABBITMQ_PASSWORD', 'admin'),
    "queue": os.getenv('QUEUE_NAME', 'product_queue'),
    "port": 5672
}





    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,         # Número máximo de conexiones abiertas
        "max_overflow": 5,       # Conexiones adicionales si el pool está lleno
        "pool_timeout": 30,      # Tiempo máximo para esperar una conexión antes de error
        "pool_recycle": 1800     # Reciclar conexiones cada 30 minutos
    }
