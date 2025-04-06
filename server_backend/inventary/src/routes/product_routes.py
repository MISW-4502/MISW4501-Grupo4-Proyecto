from flask import Blueprint, request, jsonify
from src.services.product_service import (
    process_excel_and_save,
    list_products,
    update_product,
    delete_product,
    create_product
)


inventary_bp = Blueprint('invetary', __name__)

@inventary_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "server inventary corriendo"}), 200


@inventary_bp.route('/upload-products', methods=['POST'])
def upload_products():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        result = process_excel_and_save(file)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inventary_bp.route('/products', methods=['POST'])
def create_product_endpoint():
    data = request.get_json()
    result, error = create_product(data)
    if error:
        return jsonify({'error': error}), 400
    return jsonify(result), 201


@inventary_bp.route('/products', methods=['GET'])
def get_all_products():
    try:
        result = list_products()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inventary_bp.route('/products/<int:product_id>', methods=['PUT'])
def edit_product(product_id):
    data = request.get_json()
    result, error = update_product(product_id, data)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(result), 200


@inventary_bp.route('/products/<int:product_id>', methods=['DELETE'])
def remove_product(product_id):
    success, error = delete_product(product_id)
    if not success:
        return jsonify({'error': error}), 404
    return jsonify({'message': 'Producto eliminado correctamente'}), 200

