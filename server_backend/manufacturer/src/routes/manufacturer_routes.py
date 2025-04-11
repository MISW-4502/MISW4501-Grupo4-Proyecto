from flask import Blueprint, request, jsonify
from src.services.manufacturer_service import (
    create_manufacturer,
    edit_manufacturer,
    delete_manufacturer,
    list_manufacturers,
    get_manufacturer_by_id
)

manufacturer_bp = Blueprint('manufacturer', __name__)

@manufacturer_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok"}), 200

@manufacturer_bp.route('/manufacturers', methods=['POST'])
def create():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requerido"}), 400
    result, status = create_manufacturer(data)
    return jsonify(result), status

@manufacturer_bp.route('/manufacturers/<int:manufacturer_id>', methods=['PUT'])
def update(manufacturer_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requerido"}), 400
    result, status = edit_manufacturer(data, manufacturer_id)
    return jsonify(result), status

@manufacturer_bp.route('/manufacturers/<int:manufacturer_id>', methods=['DELETE'])
def remove(manufacturer_id):
    result, status = delete_manufacturer(manufacturer_id)
    return jsonify(result), status

@manufacturer_bp.route('/manufacturers', methods=['GET'])
def get_all():
    result, status = list_manufacturers()
    return jsonify(result), status

@manufacturer_bp.route('/manufacturers/<int:manufacturer_id>', methods=['GET'])
def get_by_id(manufacturer_id):
    result, status = get_manufacturer_by_id(manufacturer_id)
    return jsonify(result), status
