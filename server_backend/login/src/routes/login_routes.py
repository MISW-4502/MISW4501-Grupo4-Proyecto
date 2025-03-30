from flask import Blueprint, request, jsonify
from src.services.login_service import process_login

login_route = Blueprint('login', __name__)

@login_route.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    process_login(username, password)
    return jsonify({"message": "Login enviado para validación"}), 202


@login_route.route('/ping', methods=['GET'])
def ping():
    return 'pong', 200

   