from flask import Blueprint, request, jsonify
from src.services.sales_producer import publish_order_to_queue
from src.services.sales_service import (
    
    editOrder,
    getOrderById,
    getOrders,
    editOrAddItemsOrder,
    eliminatedOrder,
    eliminateItemOrder,
    getOrdersByClientId,
    getOrdersBySellerId
)

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "server sales corriendo"}), 200


@sales_bp.route('/sales', methods=['POST'])
def create_order():
    data = request.get_json()

    # ✅ Validaciones del body
    if not isinstance(data, dict):
        return jsonify({"error": "El cuerpo debe ser un JSON"}), 400

    if not data.get("id_cliente"):
        return jsonify({"error": "Falta el campo 'id_cliente'"}), 400

    if not isinstance(data.get("detalles"), list) or not data["detalles"]:
        return jsonify({"error": "El campo 'detalles' debe ser una lista con al menos un item"}), 400

    # ✅ Validar campos por cada item en detalles
    for i, item in enumerate(data["detalles"]):
        if not all(k in item for k in ("id_producto", "cantidad", "precio_unitario")):
            return jsonify({"error": f"Faltan campos en el detalle #{i + 1}"}), 400

    # ✅ Enviar a la cola RabbitMQ
    publish_order_to_queue(data)

    return jsonify({"message": "Pedido en proceso"}), 202


@sales_bp.route('/sales', methods=['GET'])
def list_orders():
    return jsonify(getOrders()), 200

@sales_bp.route('/sales/<int:pedido_id>', methods=['GET'])
def get_order(pedido_id):
    pedido = getOrderById(pedido_id)
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404
    return jsonify(pedido), 200


@sales_bp.route('/sales/<int:pedido_id>', methods=['PATCH'])
def update_order(pedido_id):
    data = request.get_json()
    result, status = editOrder(pedido_id, data)
    return jsonify(result), status


@sales_bp.route('/sales/<int:pedido_id>/items', methods=['PATCH'])
def update_multiple_items(pedido_id):
    data = request.get_json()
    items = data.get("items")

    if not isinstance(items, list) or not items:
        return jsonify({"error": "Debes enviar una lista de items"}), 400
    result, status = editOrAddItemsOrder(pedido_id, items)
    return jsonify(result), status


@sales_bp.route('/sales/<int:pedido_id>/items/<int:id_producto>', methods=['DELETE'])
def delete_item(pedido_id, id_producto):
    result, status = eliminateItemOrder(pedido_id, id_producto)
    return jsonify(result), status


@sales_bp.route('/sales/<int:pedido_id>', methods=['DELETE'])
def delete_order(pedido_id):
    result, status = eliminatedOrder(pedido_id)
    return jsonify(result), status


@sales_bp.route('/sales/client/<int:id_cliente>', methods=['GET'])
def get_orders_by_client(id_cliente):
    pedidos = getOrdersByClientId(id_cliente)
    if not pedidos:
        return jsonify({"message": "No se encontraron pedidos para este cliente"}), 404
    return jsonify(pedidos), 200


@sales_bp.route('/sales/seller/<int:id_vendedor>', methods=['GET'])
def get_orders_by_seller(id_vendedor):
    pedidos = getOrdersBySellerId(id_vendedor)
    if not pedidos:
        return jsonify({"message": "No se encontraron pedidos para este vendedor"}), 404
    return jsonify(pedidos), 200