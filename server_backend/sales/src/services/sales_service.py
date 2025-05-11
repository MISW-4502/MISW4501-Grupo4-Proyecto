from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.config import Config
from src.models.sales_models import Pedido,DetallePedido
import requests
from decimal import Decimal


def get_session():
    engine = create_engine(
        Config.SQLALCHEMY_DATABASE_URI,
        **Config.SQLALCHEMY_ENGINE_OPTIONS
    )
    return sessionmaker(bind=engine)()


def getOrders():
    session = get_session()
    try:
        pedidos = session.query(Pedido).all()
        return [
            {
                "pedido_id": p.pedido_id,
                "id_cliente": p.id_cliente,
                "id_vendedor": p.id_vendedor,
                "fecha_creacion": p.fecha_creacion.isoformat(),
                "estado": p.estado,
                "total": float(p.total)
            } for p in pedidos
        ]
    finally:
        session.close()

def getOrderById(pedido_id,token):
    session = get_session()
    try:
        pedido = session.query(Pedido).filter_by(pedido_id=pedido_id).first()
        if not pedido:
            return None

        detalles = []
        for d in pedido.detalles:
            # Llamada al microservicio de inventario para obtener el nombre del producto
            try:
                response = requests.get(f"http://inventary-service:3400/inventary/products/{d.id_producto}",headers={"Authorization": f"Bearer {token}"},timeout=3)

                if response.status_code == 200:
                    product_data = response.json()
                    nombre_producto = product_data.get("nombre", "Nombre no disponible")
                else:
                    nombre_producto = "Producto no encontrado"
            except Exception as e:
                nombre_producto = f"Error al consultar producto: {str(e)}"
            print(f"Nombre obtenido: {nombre_producto}")
            detalles.append({
                
                "cantidad": d.cantidad,
                "id_producto": d.id_producto,
                "nombre": nombre_producto,
                "precio_unitario": float(d.precio_unitario),
                "subtotal": float(d.subtotal)
            })

        return {
            "pedido_id": pedido.pedido_id,
            "id_cliente": pedido.id_cliente,
            "id_vendedor": pedido.id_vendedor,
            "fecha_creacion": pedido.fecha_creacion.isoformat(),
            "estado": pedido.estado,
            "total": float(pedido.total),
            "detalles": detalles
        }
    finally:
        session.close()



def editOrder(pedido_id, data):
    session = get_session()
    try:
        pedido = session.query(Pedido).filter_by(pedido_id=pedido_id).first()
        if not pedido:
            return {"error": "Pedido no encontrado"}, 404

        if pedido.estado != "PENDIENTE":
            return {"error": "Solo se pueden editar pedidos en estado PENDIENTE"}, 400

        if "estado" in data:
            pedido.estado = data["estado"]

        if "id_vendedor" in data:
            pedido.id_vendedor = data["id_vendedor"]

        session.commit()
        return {"message": "Pedido actualizado correctamente"}, 200
    finally:
        session.close()  
    

def editOrAddItemsOrder(pedido_id, items):
    session = get_session()
    try:
        pedido = session.query(Pedido).filter_by(pedido_id=pedido_id).first()
        if not pedido:
            return {"error": "Pedido no encontrado"}, 404

        if pedido.estado != "PENDIENTE":
            return {"error": "Solo se pueden editar pedidos en estado PENDIENTE"}, 400

        errores = []
        nuevos = 0
        modificados = 0

        for item in items:
            id_producto = item.get("id_producto")
            cantidad = item.get("cantidad")
            precio_unitario = item.get("precio_unitario")

            if not all(isinstance(v, (int, float)) for v in [id_producto, cantidad, precio_unitario]) or cantidad <= 0:
                errores.append({"id_producto": id_producto, "error": "Datos inválidos"})
                continue

            detalle = session.query(DetallePedido).filter_by(
                id_pedido=pedido_id,
                id_producto=id_producto
            ).first()

            subtotal = Decimal(str(precio_unitario)) * Decimal(str(cantidad))

            if detalle:
                detalle.cantidad = cantidad
                detalle.precio_unitario = precio_unitario
                detalle.subtotal = subtotal
                modificados += 1
            else:
                nuevo = DetallePedido(
                    id_pedido=pedido_id,
                    id_producto=id_producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal
                )
                session.add(nuevo)
                nuevos += 1

        # Recalcular total del pedido
        pedido.total = sum(Decimal(str(d.subtotal)) for d in pedido.detalles)
        session.commit()

        response = {
            "message": "Pedido actualizado",
            "modificados": modificados,
            "agregados": nuevos
        }

        if errores:
            response["errores"] = errores
            return response, 207  # Multi-Status
        else:
            return response, 200

    finally:
        session.close()




def eliminateItemOrder(pedido_id, id_producto):
    session = get_session()
    try:
        detalle = session.query(DetallePedido).filter_by(
            id_pedido=pedido_id,
            id_producto=id_producto
        ).first()

        if not detalle:
            return {"error": "Detalle no encontrado"}, 404

        if detalle.pedido.estado != "PENDIENTE":
            return {"error": "Solo se pueden eliminar productos de pedidos PENDIENTES"}, 400

        session.delete(detalle)

        # Recalcular total del pedido
        pedido = detalle.pedido
        pedido.total = sum(d.subtotal for d in pedido.detalles if d != detalle)

        session.commit()
        return {"message": "Producto eliminado del pedido"}, 200

    finally:
        session.close()


def eliminatedOrder(pedido_id):
    session = get_session()
    try:
        pedido = session.query(Pedido).filter_by(pedido_id=pedido_id).first()
        if not pedido:
            return {"error": "Pedido no encontrado"}, 404

        if pedido.estado != "PENDIENTE":
            return {"error": "Solo se pueden eliminar pedidos en estado PENDIENTE"}, 400

        session.delete(pedido)  # esto también elimina los detalles si tienes cascade="all, delete-orphan"
        session.commit()

        return {"message": "Pedido eliminado correctamente"}, 200
    finally:
        session.close()


def getOrdersByClientId(id_cliente):
    session = get_session()
    try:
        pedidos = session.query(Pedido).filter_by(id_cliente=id_cliente).all()
        if not pedidos:
            return []

        return [
            {
                "pedido_id": p.pedido_id,
                "id_cliente": p.id_cliente,
                "id_vendedor": p.id_vendedor,
                "fecha_creacion": p.fecha_creacion.isoformat(),
                "estado": p.estado,
                "total": float(p.total),
                "detalles": [
                    {
                        "id_producto": d.id_producto,
                        "cantidad": d.cantidad,
                        "precio_unitario": float(d.precio_unitario),
                        "subtotal": float(d.subtotal)
                    } for d in p.detalles
                ]
            }
            for p in pedidos
        ]
    finally:
        session.close()


def getOrdersBySellerId(id_vendedor):
    session = get_session()
    try:
        pedidos = session.query(Pedido).filter_by(id_vendedor=id_vendedor).all()
        if not pedidos:
            return []

        return [
            {
                "pedido_id": p.pedido_id,
                "id_cliente": p.id_cliente,
                "id_vendedor": p.id_vendedor,
                "fecha_creacion": p.fecha_creacion.isoformat(),
                "estado": p.estado,
                "total": float(p.total),
                "detalles": [
                    {
                        "id_producto": d.id_producto,
                        "cantidad": d.cantidad,
                        "precio_unitario": float(d.precio_unitario),
                        "subtotal": float(d.subtotal)
                    } for d in p.detalles
                ]
            }
            for p in pedidos
        ]
    finally:
        session.close()