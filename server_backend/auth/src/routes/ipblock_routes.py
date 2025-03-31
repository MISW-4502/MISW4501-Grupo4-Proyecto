from flask import Blueprint, request, jsonify
from src.services.ipblock_service import is_ip_blocked, register_failed_attempt, reset_ip

ipblock_bp = Blueprint('ipblock', __name__)

@ipblock_bp.route('/ip/check', methods=['POST'])
def check_ip():
    ip = request.get_json().get("ip")
    if not ip:
        return jsonify({"error": "IP requerida"}), 400

    if is_ip_blocked(ip):
        return jsonify({"blocked": True}), 403
    return jsonify({"blocked": False}), 200

@ipblock_bp.route('/ip/fail', methods=['POST'])
def fail_attempt():
    ip = request.get_json().get("ip")
    if not ip:
        return jsonify({"error": "IP requerida"}), 400
    register_failed_attempt(ip)
    return jsonify({"message": "Intento registrado"}), 200

@ipblock_bp.route('/ip/reset', methods=['POST'])
def reset_attempts():
    ip = request.get_json().get("ip")
    if not ip:
        return jsonify({"error": "IP requerida"}), 400
    reset_ip(ip)
    return jsonify({"message": "Intentos reiniciados"}), 200
