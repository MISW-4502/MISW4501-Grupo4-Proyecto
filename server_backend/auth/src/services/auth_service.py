from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.user_model import User
from src.config.config import Config

# Usa la URI y las opciones directamente desde el config
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    **Config.SQLALCHEMY_ENGINE_OPTIONS
)

SessionLocal = sessionmaker(bind=engine)

def authenticate_user(username, password):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username, password=password).first()
        return user is not None
    finally:
        session.close()
