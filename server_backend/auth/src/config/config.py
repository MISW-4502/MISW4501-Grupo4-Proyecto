import os


class Config:
    JWT_SECRET = os.getenv("JWT_SECRET", "supersecreta123")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 1)) 
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,         # Número máximo de conexiones abiertas
        "max_overflow": 5,       # Conexiones adicionales si el pool está lleno
        "pool_timeout": 30,      # Tiempo máximo para esperar una conexión antes de error
        "pool_recycle": 1800     # Reciclar conexiones cada 30 minutos
    }
