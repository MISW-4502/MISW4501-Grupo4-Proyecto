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


def process_excel_and_save(file):
   
    try:
        df = pd.read_excel(file)

        required_columns = {'name', 'price', 'quantity', 'manufacturer', 'location'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Faltan columnas requeridas. Se requieren: {required_columns}")

        errors = []
        valid_products = []

        for index, row in df.iterrows():
            try:
                # Validaciones básicas
                if pd.isna(row['name']) or pd.isna(row['price']) or pd.isna(row['quantity']):
                    raise ValueError("Campos obligatorios vacíos (name, price o quantity).")

                if not isinstance(row['price'], (int, float)):
                    raise ValueError("Precio no es un número válido.")

                if not isinstance(row['quantity'], (int, float)):
                    raise ValueError("Cantidad no es un número válido.")

                product = Product(
                    name=str(row['name']),
                    price=float(row['price']),
                    quantity=int(row['quantity']),
                    manufacturer=str(row['manufacturer']) if not pd.isna(row['manufacturer']) else None,
                    location=str(row['location']) if not pd.isna(row['location']) else None
                )

                valid_products.append(product)

            except Exception as e:
                errors.append(f"Fila {index + 2}: {str(e)}")  # +2 por encabezado y 0-index
        

        if valid_products:
            records = df.to_dict(orient='records')
            publish_to_queue(records)

        return {
            "enviados_a_cola": len(valid_products),
            "errores": errors
        }


    except Exception as e:
        return {"error": str(e)}
 

def create_product(data):
    session = SessionLocal()
    try:
        name = data.get('name')
        price = data.get('price')
        quantity = data.get('quantity')

        if not name or price is None or quantity is None:
            return None, "Campos 'name', 'price' y 'quantity' son obligatorios"

        product = Product(
            name=name,
            price=float(price),
            quantity=int(quantity),
            manufacturer=data.get('manufacturer'),
            location=data.get('location')
        )

        session.add(product)
        session.commit()

        return {
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "quantity": product.quantity,
            "manufacturer": product.manufacturer,
            "location": product.location,
            "created_at": product.created_at.isoformat() if product.created_at else None
        }, None
    except Exception as e:
        session.rollback()
        return None, str(e)
    finally:
        session.close()


def list_products():
    session = SessionLocal()
    try:
        products = session.query(Product).all()
        result = [
            {
                "id": p.id,
                "name": p.name,
                "price": float(p.price),
                "quantity": p.quantity,
                "manufacturer": p.manufacturer,
                "location": p.location,
                "created_at": p.created_at.isoformat() if p.created_at else None
            } for p in products
        ]
        return result
    finally:
        session.close()


def update_product(product_id, data):
    session = SessionLocal()
    try:
        product = session.query(Product).get(product_id)
        if not product:
            return None, "Producto no encontrado"

        product.name = data.get('name', product.name)
        product.price = data.get('price', product.price)
        product.quantity = data.get('quantity', product.quantity)
        product.manufacturer = data.get('manufacturer', product.manufacturer)
        product.location = data.get('location', product.location)

        session.commit()
        return {
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "quantity": product.quantity,
            "manufacturer": product.manufacturer,
            "location": product.location,
            "created_at": product.created_at.isoformat() if product.created_at else None
        }, None
    except Exception as e:
        session.rollback()
        return None, str(e)
    finally:
        session.close()


def delete_product(product_id):
    session = SessionLocal()
    try:
        product = session.query(Product).get(product_id)
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
