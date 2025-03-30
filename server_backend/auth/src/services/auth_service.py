import datetime
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.user_model import User
from src.config.config import Config

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

def generate_token(username):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    payload = {
        "sub": username,
        "exp": expiration
    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")
    return token
