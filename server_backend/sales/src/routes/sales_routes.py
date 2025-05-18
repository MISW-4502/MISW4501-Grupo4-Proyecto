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
    getOrdersBySellerId,
    reservar_stock,
    liberar_stock
)
from src.utils.auth_utils import token_required_remote,get_token_from_request



sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "server sales corriendo"}), 200


@sales_bp.route('/sales', methods=['POST'])
@token_required_remote
def create_order():
    data = request.get_json()
    token = get_token_from_request()

    if not isinstance(data, dict):
        return jsonify({"error": "El cuerpo debe ser un JSON"}), 400

    if not data.get("id_cliente"):
        return jsonify({"error": "Falta el campo 'id_cliente'"}), 400

    if not isinstance(data.get("detalles"), list) or not data["detalles"]:
        return jsonify({"error": "El campo 'detalles' debe ser una lista con al menos un item"}), 400

    errores = []
    reservas = []

    # 1. Intentar reservar stock por cada producto
    for i, item in enumerate(data["detalles"]):
        if not all(k in item for k in ("id_producto", "cantidad", "precio_unitario")):
            errores.append({"detalle": i + 1, "error": "Faltan campos obligatorios"})
            continue

        id_producto = item["id_producto"]
        cantidad = item["cantidad"]

        success, error = reservar_stock(id_producto, cantidad, token)
        if success:
            reservas.append({"id_producto": id_producto, "cantidad": cantidad})
        else:
            errores.append({"id_producto": id_producto, "error": error or "Stock insuficiente"})

    if errores:
        return jsonify({"error": "No se pudo crear el pedido", "detalles": errores}), 409

    # 2. Intentar publicar a la cola
    try:
        publish_order_to_queue(data)
        return jsonify({"message": "Pedido en proceso"}), 202

    except Exception as e:
        # 3. Rollback: liberar stock previamente reservado
        rollback_errores = []
        for r in reservas:
            ok, liberar_error = liberar_stock(r["id_producto"], r["cantidad"], token)
            if not ok:
                rollback_errores.append({
                    "id_producto": r["id_producto"],
                    "error": liberar_error or "Error liberando stock"
                })

        return jsonify({
            "error": "Error al publicar el pedido. Se revirtió el stock.",
            "detalle_error": str(e),
            "rollback_errores": rollback_errores
        }), 500

@sales_bp.route('/sales', methods=['GET'])
@token_required_remote
def list_orders():
    return jsonify(getOrders()), 200

@sales_bp.route('/sales/<int:pedido_id>', methods=['GET'])
@token_required_remote
def get_order(pedido_id):
    token = get_token_from_request()
    pedido = getOrderById(pedido_id,token)
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404
    return jsonify(pedido), 200


@sales_bp.route('/sales/<int:pedido_id>', methods=['PATCH'])
@token_required_remote
def update_order(pedido_id):
    data = request.get_json()
    result, status = editOrder(pedido_id, data)
    return jsonify(result), status


@sales_bp.route('/sales/<int:pedido_id>/items', methods=['PATCH'])
@token_required_remote
def update_multiple_items(pedido_id):
    data = request.get_json()
    items = data.get("items")

    if not isinstance(items, list) or not items:
        return jsonify({"error": "Debes enviar una lista de items"}), 400
    token = get_token_from_request()
    result, status = editOrAddItemsOrder(pedido_id, items,token)
    return jsonify(result), status


@sales_bp.route('/sales/<int:pedido_id>/items/<int:id_producto>', methods=['DELETE'])
@token_required_remote
def delete_item(pedido_id, id_producto):
    token = get_token_from_request()
    result, status = eliminateItemOrder(pedido_id, id_producto,token)
    return jsonify(result), status


@sales_bp.route('/sales/<int:pedido_id>', methods=['DELETE'])
@token_required_remote
def delete_order(pedido_id):
    token = get_token_from_request()
    result, status = eliminatedOrder(pedido_id,token)
    return jsonify(result), status


@sales_bp.route('/sales/client/<int:id_cliente>', methods=['GET'])
@token_required_remote
def get_orders_by_client(id_cliente):
    pedidos = getOrdersByClientId(id_cliente)
    if not pedidos:
        return jsonify({"message": "No se encontraron pedidos para este cliente"}), 404
    return jsonify(pedidos), 200


@sales_bp.route('/sales/seller/<int:id_vendedor>', methods=['GET'])
@token_required_remote
def get_orders_by_seller(id_vendedor):
    pedidos = getOrdersBySellerId(id_vendedor)
    if not pedidos:
        return jsonify({"message": "No se encontraron pedidos para este vendedor"}), 404
    return jsonify(pedidos), 200