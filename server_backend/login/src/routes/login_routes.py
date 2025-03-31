from flask import Blueprint, request, jsonify
from src.services.login_service import process_login

login_route = Blueprint('login', __name__)


@login_route.route('/ping', methods=['GET'])
def ping():
    return 'pong', 200

   