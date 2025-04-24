import requests
from flask import request, jsonify
from functools import wraps
import os

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:3200")  # ajusta el puerto si es otro

def token_required_remote(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Token requerido"}), 401

        try:
            response = requests.post(f"{AUTH_SERVICE_URL}/auth/validate", json={"token": token}, timeout=3)
            if response.status_code != 200 or not response.json().get("valid"):
                return jsonify({"error": "Token inválido"}), 401
            request.user_data = response.json()  # opcional, si quieres usar sub/nombre
        except requests.RequestException:
            return jsonify({"error": "No se pudo validar el token"}), 503

        return f(*args, **kwargs)

    return decorated
