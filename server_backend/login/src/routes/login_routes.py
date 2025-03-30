from flask import Blueprint, request, jsonify
from src.services.login_service import process_login

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    process_login(username, password)
    return jsonify({"message": "Login enviado para validación"}), 202
