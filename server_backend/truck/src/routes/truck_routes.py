from flask import Blueprint, request, jsonify
from src.services.truck_service import create_truck, edit_truck, delete_truck,list_trucks,get_truck_by_id
from src.utils.auth_utils import token_required_remote


trucks_bp = Blueprint('trucks', __name__)

@trucks_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok"}), 200

@trucks_bp.route('/trucks', methods=['POST'])
@token_required_remote
def create_trucks():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    result, status = create_truck(data)
    return jsonify(result), status



@trucks_bp.route('/trucks/<int:truck_id>', methods=['PUT'])
@token_required_remote
def update_truck(truck_id):

    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    result, status = edit_truck(data, truck_id)
    return jsonify(result), status


@trucks_bp.route('/trucks/<int:truck_id>', methods=['DELETE'])
@token_required_remote
def remove_truck(truck_id):

    result, status = delete_truck(truck_id)
    return jsonify(result), status

@trucks_bp.route('/trucks', methods=['GET'])
@token_required_remote
def get_all_trucks():
    result, status = list_trucks()
    return jsonify(result), status


@trucks_bp.route('/trucks/<int:truck_id>', methods=['GET'])
@token_required_remote
def get_truck(truck_id):
    result, status = get_truck_by_id(truck_id)
    return jsonify(result), status
