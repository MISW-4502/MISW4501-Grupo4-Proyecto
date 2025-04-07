import pandas as pd
import json
import pika
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.config import Config
from src.models.product_model import Product
from src.services.producer import publish_to_queue

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    **Config.SQLALCHEMY_ENGINE_OPTIONS
)

SessionLocal = sessionmaker(bind=engine)


import pandas as pd

def process_excel_and_save(file):
    try:
        filename = file.filename.lower()

        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            raise ValueError("Formato de archivo no soportado. Debe ser .csv, .xls o .xlsx")

        required_columns = {'nombre', 'precio_unitario', 'cantidad', 'descripcion', 'tipo', 'ubicacion'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Faltan columnas requeridas. Se requieren: {required_columns}")

        errors = []
        valid_products = []

        for index, row in df.iterrows():
            try:
                if pd.isna(row['nombre']) or pd.isna(row['precio_unitario']):
                    raise ValueError("Campos obligatorios vacíos (nombre o precio_unitario).")

                product = {
                    "nombre": str(row['nombre']),
                    "precio_unitario": float(row['precio_unitario']),
                    "cantidad": int(row['cantidad']) if not pd.isna(row['cantidad']) else 0,
                    "descripcion": str(row['descripcion']) if not pd.isna(row['descripcion']) else None,
                    "tipo": str(row['tipo']) if not pd.isna(row['tipo']) else None,
                    "ubicacion": str(row['ubicacion']) if not pd.isna(row['ubicacion']) else None
                }

                valid_products.append(product)

            except Exception as e:
                errors.append(f"Fila {index + 2}: {str(e)}")

        if valid_products:
            publish_to_queue(valid_products)

        return {
            "enviados_a_cola": len(valid_products),
            "errores": errors
        }

    except Exception as e:
        return {"error": str(e)}


def create_product(data):
    session = SessionLocal()
    try:
        nombre = data.get('nombre')
        precio = data.get('precio_unitario')

        if not nombre or precio is None:
            return None, "Campos 'nombre' y 'precio_unitario' son obligatorios"

        product = Product(
            nombre=nombre,
            descripcion=data.get('descripcion'),
            precio_unitario=float(precio),
            tipo=data.get('tipo'),
            cantidad=int(data.get('cantidad', 0)),
            ubicacion=data.get('ubicacion')
        )

        session.add(product)
        session.commit()

        return {
            "producto_id": product.producto_id,
            "nombre": product.nombre,
            "precio_unitario": float(product.precio_unitario),
            "cantidad": product.cantidad,
            "descripcion": product.descripcion,
            "tipo": product.tipo,
            "ubicacion": product.ubicacion,
            "creado_en": product.creado_en.isoformat() if product.creado_en else None
        }, None
    except Exception as e:
        session.rollback()
        return None, str(e)
    finally:
        session.close()


def list_products(product_id=None):
    session = SessionLocal()
    try:
        if product_id:
            # Fetch a specific product by ID
            product = session.query(Product).get(product_id)
            if not product:
                return None, "Producto no encontrado"
            return {
                "producto_id": product.producto_id,
                "nombre": product.nombre,
                "precio_unitario": float(product.precio_unitario) if product.precio_unitario else None,
                "cantidad": product.cantidad,
                "descripcion": product.descripcion,
                "tipo": product.tipo,
                "ubicacion": product.ubicacion,
                "creado_en": product.creado_en.isoformat() if product.creado_en else None
            }, None
        else:
            # Fetch all products
            products = session.query(Product).all()
            return [
                {
                    "producto_id": p.producto_id,
                    "nombre": p.nombre,
                    "precio_unitario": float(p.precio_unitario) if p.precio_unitario else None,
                    "cantidad": p.cantidad,
                    "descripcion": p.descripcion,
                    "tipo": p.tipo,
                    "ubicacion": p.ubicacion,
                    "creado_en": p.creado_en.isoformat() if p.creado_en else None
                } for p in products
            ], None
    finally:
        session.close()


def update_product(producto_id, data):
    session = SessionLocal()
    try:
        product = session.query(Product).get(producto_id)
        if not product:
            return None, "Producto no encontrado"

        product.nombre = data.get('nombre', product.nombre)
        product.descripcion = data.get('descripcion', product.descripcion)
        product.precio_unitario = data.get('precio_unitario', product.precio_unitario)
        product.tipo = data.get('tipo', product.tipo)
        product.cantidad = data.get('cantidad', product.cantidad)
        product.ubicacion = data.get('ubicacion', product.ubicacion)

        session.commit()
        return {
            "producto_id": product.producto_id,
            "nombre": product.nombre,
            "precio_unitario": float(product.precio_unitario),
            "cantidad": product.cantidad,
            "descripcion": product.descripcion,
            "tipo": product.tipo,
            "ubicacion": product.ubicacion,
            "creado_en": product.creado_en.isoformat() if product.creado_en else None
        }, None
    except Exception as e:
        session.rollback()
        return None, str(e)
    finally:
        session.close()

        
def delete_product(producto_id):
    session = SessionLocal()
    try:
        product = session.query(Product).get(producto_id)
        if not product:
            return False, "Producto no encontrado"

        session.delete(product)
        session.commit()
        return True, None
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()
