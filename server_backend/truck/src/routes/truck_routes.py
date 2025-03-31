from flask import Blueprint, request, jsonify
from src.services.truck_service import create_truck


trucks_bp = Blueprint('trucks', __name__)

@trucks_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok"}), 200



@trucks_bp.route('/trucks', methods=['POST'])  
def create_trucks():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requerido"}), 400
    
    result, status = create_truck(data)  # 👈 obtenemos tupla
    return jsonify(result), status

    

    db = SessionLocal()
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if not truck:
        db.close()
        return jsonify({"error": "Not found"}), 404
    db.delete(truck)
    db.commit()
    db.close()
    return jsonify({"message": "Deleted"})
