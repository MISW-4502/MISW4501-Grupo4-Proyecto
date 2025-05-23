from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.config import Config
from src.models.sales_models import Pedido,DetallePedido
import requests
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor

INVENTARY_SERVICE_URL = "http://inventary-service:3400"
HEADERS = lambda token: {"Authorization": f"Bearer {token}"}


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



import requests

def getOrderById(pedido_id, token):
    session = get_session()
    try:
        pedido = session.query(Pedido).filter_by(pedido_id=pedido_id).first()
        if not pedido:
            return None

        producto_ids = [d.id_producto for d in pedido.detalles]

        # Solicitud optimizada al inventary-service con múltiples IDs
        try:
            response = requests.get(
                "http://inventary-service:3400/inventary/products",
                headers={"Authorization": f"Bearer {token}"},
                params={"ids": ",".join(map(str, producto_ids))},
                timeout=3
            )

            if response.status_code == 200:
                productos = response.json()
                productos_dict = {p["producto_id"]: p["nombre"] for p in productos}
            else:
                productos_dict = {}
        except Exception as e:
            productos_dict = {}

        detalles = []
        for d in pedido.detalles:
            nombre_producto = productos_dict.get(d.id_producto, "Nombre no disponible")
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
    

def editOrAddItemsOrder(pedido_id, items ,token):
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
            id_pedido=pedido_id,id_producto=id_producto).first()

            subtotal = Decimal(str(precio_unitario)) * Decimal(str(cantidad))

            if detalle:
                diferencia = cantidad - detalle.cantidad
                if diferencia > 0:
                    success, error = reservar_stock(id_producto, diferencia, token)
                    if not success:
                        errores.append({"id_producto": id_producto, "error": error or "No se pudo reservar stock"})
                        continue
                elif diferencia < 0:
                    liberar_stock(id_producto, abs(diferencia), token)

                detalle.cantidad = cantidad
                detalle.precio_unitario = precio_unitario
                detalle.subtotal = subtotal
                modificados += 1
            else:
                success, error = reservar_stock(id_producto, cantidad, token)
                if not success:
                    errores.append({"id_producto": id_producto, "error": error or "No se pudo reservar stock"})
                    continue
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


def eliminateItemOrder(pedido_id, id_producto, token):
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
        liberar_stock(id_producto, detalle.cantidad, token)

        # Recalcular total del pedido
        pedido = detalle.pedido
        pedido.total = sum(d.subtotal for d in pedido.detalles if d != detalle)

        session.commit()
        return {"message": "Producto eliminado del pedido"}, 200

    finally:
        session.close()


def eliminatedOrder(pedido_id,token):
    session = get_session()
    try:
        pedido = session.query(Pedido).filter_by(pedido_id=pedido_id).first()
        if not pedido:
            return {"error": "Pedido no encontrado"}, 404

        if pedido.estado != "PENDIENTE":
            return {"error": "Solo se pueden eliminar pedidos en estado PENDIENTE"}, 400

        for detalle in pedido.detalles:
            liberar_stock(detalle.id_producto, detalle.cantidad, token)

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


def getOrdersBySellerId(id_vendedor):\

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


def reservar_stock(id_producto, cantidad, token):
    try:
        res = requests.post(
           f"{INVENTARY_SERVICE_URL}/inventary/products/{id_producto}/reserve",
            json={"cantidad": cantidad},
            headers={"Authorization": f"Bearer {token}"},
            timeout=3
        )
        if res.status_code == 200:
            return True, None
        else:
            try:
                error = res.json().get("error", f"Status {res.status_code}")
            except ValueError:
                error = f"Respuesta inválida del inventario: {res.text}"
            return False, error
    except Exception as e:
        return False, str(e)


def liberar_stock(id_producto, cantidad, token):
    try:
        res = requests.post(
            f"{INVENTARY_SERVICE_URL}/inventary/products/{id_producto}/release",
            json={"cantidad": cantidad},
            headers=HEADERS(token),
            timeout=3
        )
        if res.status_code == 200:
            return True, None
        else:
            try:
                error = res.json().get("error", f"Status {res.status_code}")
            except ValueError:
                error = f"Respuesta inválida del inventario: {res.text}"
            return False, error   


    except Exception as e:
        return False, str(e)