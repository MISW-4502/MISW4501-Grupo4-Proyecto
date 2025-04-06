from flask import Blueprint, request, jsonify
from src.services.truck_service import create_truck, edit_truck, delete_truck,list_trucks

trucks_bp = Blueprint('trucks', __name__)

@trucks_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok"}), 200

@trucks_bp.route('/trucks', methods=['POST'])
def create_trucks():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    result, status = create_truck(data)
    return jsonify(result), status



@trucks_bp.route('/trucks/<int:truck_id>', methods=['PUT'])
def update_truck(truck_id):

    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    result, status = edit_truck(data, truck_id)
    return jsonify(result), status


@trucks_bp.route('/trucks/<int:truck_id>', methods=['DELETE'])
def remove_truck(truck_id):

    result, status = delete_truck(truck_id)
    return jsonify(result), status

@trucks_bp.route('/trucks', methods=['GET'])
def get_all_trucks():
    result, status = list_trucks()
    return jsonify(result), status
