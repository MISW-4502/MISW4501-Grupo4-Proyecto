from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)

# Health check
@auth_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok"}), 200

# Endpoint para validación (mock por ahora)
@auth_bp.route('/validate', methods=['POST'])
def validate_token():
    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify({"error": "Token requerido"}), 400

    # Aquí pondrías tu lógica real de validación de token
    if token == "fake-token-valido":
        return jsonify({"valid": True, "user_id": 123}), 200
    else:
        return jsonify({"valid": False}), 401
