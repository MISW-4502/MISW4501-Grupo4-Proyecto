from flask import Blueprint, request, jsonify
from src.services.auth_service import authenticate_user, generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok"}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "username y password son requeridos"}), 400

    if authenticate_user(username, password):
        token = generate_token(username)
        return jsonify({"token": token}), 200
    else:
        return jsonify({"error": "Credenciales inválidas"}), 401


@auth_bp.route('/validate', methods=['POST'])
def validate_token():
    from jwt import ExpiredSignatureError, InvalidTokenError
    import jwt

    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify({"error": "Token requerido"}), 400

    try:
        from src.config.config import Config
        decoded = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        return jsonify({"valid": True, "username": decoded.get("sub")}), 200
    except ExpiredSignatureError:
        return jsonify({"valid": False, "error": "Token expirado"}), 401
    except InvalidTokenError:
        return jsonify({"valid": False, "error": "Token inválido"}), 401
