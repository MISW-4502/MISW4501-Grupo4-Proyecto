import jwt
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.truck_model import Truck
from src.config.config import Config


def get_session():
    engine = create_engine(
        Config.SQLALCHEMY_DATABASE_URI,
        **Config.SQLALCHEMY_ENGINE_OPTIONS
    )
    return sessionmaker(bind=engine)()

def create_truck(data):
    session = get_session()
    try:
        # Validar placa única
        existing_truck = session.query(Truck).filter_by(placa=data['placa']).first()
        if existing_truck:
            return {"error": "Ya existe un camión con esta placa"}, 409

        truck = Truck(
            placa=data['placa'],
            capacidad=data['capacidad'],
            tipo=data.get('tipo'),
            rutas=data.get('rutas')
        )

        session.add(truck)
        session.commit()
        session.refresh(truck)

        response = {
            "camion_id": truck.camion_id,
            "placa": truck.placa,
            "capacidad": float(truck.capacidad),
            "tipo": truck.tipo,
            "fecha_registro": truck.fecha_registro.isoformat() if truck.fecha_registro else None,
            "rutas": truck.rutas
        }

        return {"message": "Camión registrado", "camion": response}, 201

    except Exception as e:
        session.rollback()
        return {"error": f"Error al registrar camión: {str(e)}"}, 500
    finally:
        session.close()


def edit_truck(data, id):
    session = get_session()
    try:
        truck = session.query(Truck).filter(Truck.camion_id == id).first()
        if not truck:
            return {"error": "Camión no encontrado"}, 404

        if 'placa' in data and data['placa'] != truck.placa:
            existing = session.query(Truck).filter(
                Truck.placa == data['placa'],
                Truck.camion_id != id
            ).first()
            if existing:
                return {"error": "Ya existe otro camión con esta placa"}, 409
            truck.placa = data['placa']

        if 'capacidad' in data:
            truck.capacidad = data['capacidad']
        if 'tipo' in data:
            truck.tipo = data['tipo']
        if 'rutas' in data:
            truck.rutas = data['rutas']

        session.commit()
        session.refresh(truck)

        response = {
            "camion_id": truck.camion_id,
            "placa": truck.placa,
            "capacidad": float(truck.capacidad),
            "tipo": truck.tipo,
            "fecha_registro": truck.fecha_registro.isoformat() if truck.fecha_registro else None,
            "rutas": truck.rutas
        }

        return {"message": "Camión actualizado", "camion": response}, 200

    except Exception as e:
        session.rollback()
        return {"error": f"Error al editar el camión: {str(e)}"}, 500
    finally:
        session.close()


def delete_truck(id):
    session = get_session()
    try:
        truck = session.query(Truck).filter(Truck.camion_id == id).first()
        if not truck:
            return {"error": "Camión no encontrado"}, 404

        session.delete(truck)
        session.commit()
        return {"message": "Camión eliminado exitosamente"}, 200

    except Exception as e:
        session.rollback()
        return {"error": f"Error al eliminar el camión: {str(e)}"}, 500
    finally:
        session.close()


def list_trucks():
    session = get_session()
    try:
        trucks = session.query(Truck).all()
        result = []
        for truck in trucks:
            result.append({
                "camion_id": truck.camion_id,
                "placa": truck.placa,
                "capacidad": float(truck.capacidad),
                "tipo": truck.tipo,
                "fecha_registro": truck.fecha_registro.isoformat() if truck.fecha_registro else None,
                "rutas": truck.rutas
            })

        return {"camiones": result}, 200

    except Exception as e:
        return {"error": f"Error al listar camiones: {str(e)}"}, 500
    finally:
        session.close()


def get_truck_by_id(truck_id):
    session = get_session()
    try:
        truck = session.query(Truck).filter(Truck.camion_id == truck_id).first()
        if not truck:
            return {"error": "Camión no encontrado"}, 404

        response = {
            "camion_id": truck.camion_id,
            "placa": truck.placa,
            "capacidad": float(truck.capacidad),
            "tipo": truck.tipo,
            "fecha_registro": truck.fecha_registro.isoformat() if truck.fecha_registro else None,
            "rutas": truck.rutas
        }

        return response, 200

    except Exception as e:
        return {"error": f"Error al obtener camión: {str(e)}"}, 500
    finally:
        session.close()
