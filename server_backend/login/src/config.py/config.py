import os

class Config:
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
