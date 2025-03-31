import datetime
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.user_model import User
from src.config.config import Config
from src.services.ipblock_service import is_ip_blocked, register_failed_attempt, reset_ip



engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    **Config.SQLALCHEMY_ENGINE_OPTIONS
)

SessionLocal = sessionmaker(bind=engine)


def login_user(username, password, ip):
    if is_ip_blocked(ip):
        return {"error": "IP bloqueada por múltiples intentos fallidos"}, 403

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username, password=password).first()
        if not user:
            register_failed_attempt(ip)
            return {"error": "Credenciales inválidas"}, 401

        reset_ip(ip)  # login exitoso, limpia intentos
        token = generate_token(username)
        return {"token": token}, 200
    finally:
        session.close()

        
def register_user(username, password, ip):
    if is_ip_blocked(ip):
        return {"error": "IP bloqueada por múltiples intentos fallidos"}, 403

    session = SessionLocal()

    try:
        # Verificar si ya existe
        user = session.query(User).filter_by(username=username).first()
        if user:
            return {"error": "El usuario ya existe"}, 409

        new_user = User(username=username, password=password)
        session.add(new_user)
        session.commit()

        # Token inmediato tras registro
        token = generate_token(username)
        return {"message": "Usuario registrado", "token": token}, 201
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
