import jwt
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.truck_model import Truck
from src.config.config import Config

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    **Config.SQLALCHEMY_ENGINE_OPTIONS
)

SessionLocal = sessionmaker(bind=engine)

def create_truck(data):
    session = SessionLocal()
    try:
        # Verificar si ya existe un camión con la misma placa
        existing_truck = session.query(Truck).filter_by(license_plate=data['license_plate']).first()
        if existing_truck:
            return {"error": "Ya existe un camión con esta placa"}, 409  # 409 Conflict

        truck = Truck(
            license_plate=data['license_plate'],
            model=data['model'],
            brand=data['brand'],
            status=data.get('status', 'ACTIVE')
        )

        session.add(truck)
        session.commit()
        session.refresh(truck)

        response = {
            "id": truck.id,
            "license_plate": truck.license_plate,
            "model": truck.model,
            "brand": truck.brand,
            "status": truck.status
        }

        return {"message": "Camión registrado", "truck": response}, 201

    except Exception as e:
        session.rollback()
        return {"error": f"Error al registrar camión: {str(e)}"}, 500
    finally:
        session.close()


def edit_truck(data, id):
    session = SessionLocal()
    try:
        truck = session.query(Truck).filter(Truck.id == id).first()
        if not truck:
            return {"error": "Camión no encontrado"}, 404

        # Validar que la nueva license_plate no esté en otro camión
        if 'license_plate' in data and data['license_plate'] != truck.license_plate:
            existing = session.query(Truck).filter(
                Truck.license_plate == data['license_plate'],
                Truck.id != id  # 👈 excluir el camión actual
            ).first()
            if existing:
                return {"error": "Ya existe otro camión con esta placa"}, 409

            truck.license_plate = data['license_plate']

        if 'model' in data:
            truck.model = data['model']
        if 'brand' in data:
            truck.brand = data['brand']
        if 'status' in data:
            truck.status = data['status']

        session.commit()
        session.refresh(truck)

        response = {
            "id": truck.id,
            "license_plate": truck.license_plate,
            "model": truck.model,
            "brand": truck.brand,
            "status": truck.status
        }

        return {"message": "Camión actualizado", "truck": response}, 200
    except Exception as e:
        session.rollback()
        return {"error": f"Error al editar el camión: {str(e)}"}, 500
    finally:
        session.close()


def delete_truck(id):
    session = SessionLocal()
    try:
        truck = session.query(Truck).filter(Truck.id == id).first()
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
    session = SessionLocal()
    try:
        trucks = session.query(Truck).all()

        result = []
        for truck in trucks:
            result.append({
                "id": truck.id,
                "license_plate": truck.license_plate,
                "model": truck.model,
                "brand": truck.brand,
                "status": truck.status,
                "created_at": truck.created_at.isoformat() if truck.created_at else None
            })

        return {"trucks": result}, 200
    except Exception as e:
        return {"error": f"Error al listar camiones: {str(e)}"}, 500
    finally:
        session.close()
