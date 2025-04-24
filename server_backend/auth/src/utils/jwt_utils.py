from functools import wraps
from flask import request, jsonify
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from src.config.config import Config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Obtener token del encabezado Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Token de autenticación requerido"}), 401

        try:
            decoded = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            request.user_data = decoded  # opcional: guardar info decodificada
        except ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        return f(*args, **kwargs)

    return decorated
