import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer

Base = declarative_base()

class Manufacturer(Base):
    __tablename__ = 'fabricante'

    fabricante_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    pais_origen = Column(String(100), nullable=True)
    creado_en = Column(DateTime, default=datetime.datetime.utcnow)
    categoria = Column(String(100), nullable=True)
