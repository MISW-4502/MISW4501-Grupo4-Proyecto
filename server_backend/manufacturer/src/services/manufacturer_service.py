from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.manufacturer_model import Manufacturer
from src.config.config import Config

def get_session():
    engine = create_engine(
        Config.SQLALCHEMY_DATABASE_URI,
        **Config.SQLALCHEMY_ENGINE_OPTIONS
    )
    return sessionmaker(bind=engine)()

def create_manufacturer(data):
    session = get_session()
    try:
        manufacturer = Manufacturer(
            nombre=data["nombre"],
            pais_origen=data.get("pais_origen"),
            categoria=data.get("categoria")
        )
        session.add(manufacturer)
        session.commit()
        session.refresh(manufacturer)
        return {
            "message": "Fabricante creado",
            "fabricante": {
                "fabricante_id": manufacturer.fabricante_id,
                "nombre": manufacturer.nombre,
                "pais_origen": manufacturer.pais_origen,
                "creado_en": manufacturer.creado_en.isoformat() if manufacturer.creado_en else None,
                "categoria": manufacturer.categoria
            }
        }, 201
    except Exception as e:
        session.rollback()
        return {"error": f"Error al crear fabricante: {str(e)}"}, 500
    finally:
        session.close()

def edit_manufacturer(data, id):
    session = get_session()
    try:
        manufacturer = session.query(Manufacturer).filter_by(fabricante_id=id).first()
        if not manufacturer:
            return {"error": "Fabricante no encontrado"}, 404

        manufacturer.nombre = data.get("nombre", manufacturer.nombre)
        manufacturer.pais_origen = data.get("pais_origen", manufacturer.pais_origen)
        manufacturer.categoria = data.get("categoria", manufacturer.categoria)

        session.commit()
        session.refresh(manufacturer)

        return {
            "message": "Fabricante actualizado",
            "fabricante": {
                "fabricante_id": manufacturer.fabricante_id,
                "nombre": manufacturer.nombre,
                "pais_origen": manufacturer.pais_origen,
                "creado_en": manufacturer.creado_en.isoformat() if manufacturer.creado_en else None,
                "categoria": manufacturer.categoria
            }
        }, 200
    except Exception as e:
        session.rollback()
        return {"error": f"Error al editar fabricante: {str(e)}"}, 500
    finally:
        session.close()

def delete_manufacturer(id):
    session = get_session()
    try:
        manufacturer = session.query(Manufacturer).filter_by(fabricante_id=id).first()
        if not manufacturer:
            return {"error": "Fabricante no encontrado"}, 404

        session.delete(manufacturer)
        session.commit()
        return {"message": "Fabricante eliminado"}, 200
    except Exception as e:
        session.rollback()
        return {"error": f"Error al eliminar fabricante: {str(e)}"}, 500
    finally:
        session.close()

def list_manufacturers():
    session = get_session()
    try:
        manufacturers = session.query(Manufacturer).all()
        result = [{
            "fabricante_id": m.fabricante_id,
            "nombre": m.nombre,
            "pais_origen": m.pais_origen,
            "creado_en": m.creado_en.isoformat() if m.creado_en else None,
            "categoria": m.categoria
        } for m in manufacturers]
        return {"fabricantes": result}, 200
    except Exception as e:
        return {"error": f"Error al listar fabricantes: {str(e)}"}, 500
    finally:
        session.close()

def get_manufacturer_by_id(id):
    session = get_session()
    try:
        m = session.query(Manufacturer).filter_by(fabricante_id=id).first()
        if not m:
            return {"error": "Fabricante no encontrado"}, 404
        return {
            "fabricante_id": m.fabricante_id,
            "nombre": m.nombre,
            "pais_origen": m.pais_origen,
            "creado_en": m.creado_en.isoformat() if m.creado_en else None,
            "categoria": m.categoria
        }, 200
    except Exception as e:
        return {"error": f"Error al obtener fabricante: {str(e)}"}, 500
    finally:
        session.close()
