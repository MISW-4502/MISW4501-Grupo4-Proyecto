import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, DateTime, Integer, Numeric

Base = declarative_base()

class Product(Base):
    __tablename__ = 'producto'  # Debe coincidir exactamente con el nombre de la tabla

    producto_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio_unitario = Column(Numeric(12, 2), nullable=True)
    creado_en = Column(DateTime, default=datetime.datetime.utcnow)
    tipo = Column(Text, nullable=True)
    cantidad = Column(Integer, nullable=True, default=0)
    ubicacion = Column(Text, nullable=True)


