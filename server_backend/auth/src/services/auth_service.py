import datetime
import bcrypt
import jwt
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.user_model import Usuario
from src.config.config import Config
from src.services.ipblock_service import is_ip_blocked, register_failed_attempt, reset_ip
from src.models.password_reset_model import PasswordReset

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    **Config.SQLALCHEMY_ENGINE_OPTIONS
)

SessionLocal = sessionmaker(bind=engine)

def hash_password(plain_password):
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def login_user(email, password, ip):
    if is_ip_blocked(ip):
        return {"error": "IP bloqueada por múltiples intentos fallidos"}, 403

    session = SessionLocal()
    try:
        user = session.query(Usuario).filter_by(email=email).first()
        if not user or not check_password(password, user.password):
            register_failed_attempt(ip)
            return {"error": "Credenciales inválidas"}, 401

        reset_ip(ip)
        token = generate_token(user.email)
        return {"token": token}, 200
    finally:
        session.close()


def register_user(email, nombre,rol, password, ip):
    if is_ip_blocked(ip):
        return {"error": "IP bloqueada por múltiples intentos fallidos"}, 403

    session = SessionLocal()
    try:
        if session.query(Usuario).filter_by(email=email).first():
            return {"error": "El email ya está registrado"}, 409

        hashed_pw = hash_password(password)
        new_user = Usuario(email=email, rol=rol ,nombre=nombre,  password=hashed_pw)
        session.add(new_user)
        session.commit()

        token = generate_token(email)
        return {"message": "Usuario registrado", "token": token}, 201
    finally:
        session.close()


def generate_token(email):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    payload = {
        "sub": email,
        "exp": expiration
    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")
    return token


def initiate_password_reset(email, ip):
    if is_ip_blocked(ip):
        return {"error": "IP bloqueada por múltiples intentos fallidos"}, 403

    session = SessionLocal()
    try:
        user = session.query(Usuario).filter_by(email=email).first()
        if not user:
            return {"error": "Usuario no encontrado"}, 404

        token = str(uuid.uuid4())
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        reset_entry = PasswordReset(email=email, token=token, expires_at=expires_at)
        session.add(reset_entry)
        session.commit()

        # TODO: llamar microservicio de envío de email
        # send_reset_email(email, token)

        return {"message": "Correo de recuperación enviado", "token": token}, 200
    finally:
        session.close()


def reset_password_by_token(token, new_password):
    session = SessionLocal()
    try:
        reset = session.query(PasswordReset).filter_by(token=token).first()
        if not reset:
            return {"error": "Token inválido"}, 400

        if reset.expires_at < datetime.datetime.utcnow():
            return {"error": "Token expirado"}, 410

        user = session.query(Usuario).filter_by(email=reset.email).first()
        if not user:
            return {"error": "Usuario no encontrado"}, 404

        user.password = hash_password(new_password)
        session.delete(reset)
        session.commit()

        return {"message": "Contraseña actualizada con éxito"}, 200
    finally:
        session.close()