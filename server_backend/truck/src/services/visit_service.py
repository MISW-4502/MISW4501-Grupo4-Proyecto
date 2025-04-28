from src.models.visita_model import Visita
from src.config.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



def get_session():
    engine = create_engine(
        Config.SQLALCHEMY_DATABASE_URI,
        **Config.SQLALCHEMY_ENGINE_OPTIONS
    )
    return sessionmaker(bind=engine)()


def create_visit(data):
    session = get_session()
    try:
        nueva_visita = Visita(
            id_vendedor=data['id_vendedor'],
            id_cliente=data['id_cliente'],
            fecha_visita=data['fecha_visita'],
            estado=data.get('estado', 'PENDIENTE'),
            descripcion=data.get('descripcion'),
            direccion=data.get('direccion')
        )
        session.add(nueva_visita)
        session.commit()
        session.refresh(nueva_visita)

        return {"message": "Visita creada exitosamente", "visita_id": nueva_visita.visita_id}, 201
    except Exception as e:
        session.rollback()
        return {"error": str(e)}, 500
    finally:
        session.close()

def get_visit_by_id(visita_id):
    session = get_session()
    try:
        visita = session.query(Visita).filter_by(visita_id=visita_id).first()
        if not visita:
            return {"error": "Visita no encontrada"}, 404
        
        return {
            "visita_id": visita.visita_id,
            "id_vendedor": visita.id_vendedor,
            "id_cliente": visita.id_cliente,
            "fecha_visita": visita.fecha_visita.isoformat(),
            "estado": visita.estado,
            "descripcion": visita.descripcion,
            "direccion": visita.direccion
        }, 200
    finally:
        session.close()

def list_visits():
    session = get_session()
    try:
        visitas = session.query(Visita).all()
        resultado = [
            {
                "visita_id": v.visita_id,
                "id_vendedor": v.id_vendedor,
                "id_cliente": v.id_cliente,
                "fecha_visita": v.fecha_visita.isoformat(),
                "estado": v.estado,
                "descripcion": v.descripcion,
                "direccion": v.direccion
            }
            for v in visitas
        ]
        return resultado, 200
    finally:
        session.close()

def update_visit(visita_id, data):
    session = get_session()
    try:
        visita = session.query(Visita).filter_by(visita_id=visita_id).first()
        if not visita:
            return {"error": "Visita no encontrada"}, 404

        for key, value in data.items():
            if hasattr(visita, key):
                setattr(visita, key, value)

        session.commit()
        return {"message": "Visita actualizada exitosamente"}, 200
    except Exception as e:
        session.rollback()
        return {"error": str(e)}, 500
    finally:
        session.close()

def delete_visit(visita_id):
    session = get_session()
    try:
        visita = session.query(Visita).filter_by(visita_id=visita_id).first()
        if not visita:
            return {"error": "Visita no encontrada"}, 404
        
        session.delete(visita)
        session.commit()
        return {"message": "Visita eliminada exitosamente"}, 200
    except Exception as e:
        session.rollback()
        return {"error": str(e)}, 500
    finally:
        session.close()


def list_visits_by_seller(id_vendedor):
    session = get_session()
    try:
        visitas = session.query(Visita).filter(Visita.id_vendedor == id_vendedor).all()

        if not visitas:
            return {"message": "No se encontraron visitas asignadas al vendedor."}, 404

        visitas_list = [
            {
                "visita_id": visita.visita_id,
                "id_cliente": visita.id_cliente,
                "fecha_visita": visita.fecha_visita.isoformat() if visita.fecha_visita else None,
                "estado": visita.estado,
                "descripcion": visita.descripcion,
                "direccion": visita.direccion
            }
            for visita in visitas
        ]

        return visitas_list,200

    finally:
        session.close()