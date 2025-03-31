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