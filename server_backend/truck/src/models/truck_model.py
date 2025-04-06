import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, Numeric, Text

Base = declarative_base()

class Truck(Base):
    __tablename__ = 'camion'

    camion_id = Column(Integer, primary_key=True, autoincrement=True)
    placa = Column(String(50), nullable=False, unique=True)
    capacidad = Column(Numeric(12, 2), nullable=False)
    tipo = Column(String(50), nullable=True)
    fecha_registro = Column(DateTime, default=datetime.datetime.utcnow)
    rutas = Column(Text, nullable=True)
