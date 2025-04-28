from flask import Blueprint, request, jsonify
from src.services.truck_service import create_truck, edit_truck, delete_truck,list_trucks,get_truck_by_id
from src.services.visit_service import create_visit, get_visit_by_id, update_visit, delete_visit, list_visits,list_visits_by_seller
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


@trucks_bp.route('/visits', methods=['POST'])
@token_required_remote
def create_visita_route():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    result, status = create_visit(data)
    return jsonify(result), status

# Obtener una visita por ID
@trucks_bp.route('/visits/<int:visita_id>', methods=['GET'])
@token_required_remote
def get_visita(visita_id):
    result, status = get_visit_by_id(visita_id)
    return jsonify(result), status

# Actualizar visita
@trucks_bp.route('/visits/<int:visita_id>', methods=['PUT'])
@token_required_remote
def update_visita_route(visita_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    result, status = update_visit(data, visita_id)
    return jsonify(result), status

# Eliminar visita
@trucks_bp.route('/visits/<int:visita_id>', methods=['DELETE'])
@token_required_remote
def delete_visita_route(visita_id):
    result, status = delete_visit(visita_id)
    return jsonify(result), status

# Listar todas las visitas
@trucks_bp.route('/visits/all', methods=['GET'])
@token_required_remote
def list_visitas_route():
    result, status = list_visits()
    return jsonify(result), status

@trucks_bp.route('/visits/seller/<int:id_vendedor>', methods=['GET'])
@token_required_remote
def list_visitas_by_vendedor_route(id_vendedor):
    result, status = list_visits_by_seller(id_vendedor)
    return jsonify(result), status