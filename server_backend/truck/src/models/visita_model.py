import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime

Base = declarative_base()

class Visita(Base):
    __tablename__ = 'visita'

    visita_id = Column(Integer, primary_key=True, autoincrement=True)
    id_vendedor = Column(Integer, nullable=False)  
    id_cliente = Column(Integer, nullable=False)  
    fecha_visita = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    estado = Column(String(50), default='PENDIENTE')
    descripcion = Column(Text, nullable=True)
    direccion = Column(Text, nullable=True)


