from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Enum
from enum import Enum as PyEnum

Base = declarative_base()

class RolEnum(PyEnum):
    ADMIN = "ADMIN"
    CLIENTE = "CLIENTE"
    VENDEDOR = "VENDEDOR"

class Usuario(Base):
    __tablename__ = 'usuario'  # Coincide con el nombre real de la tabla en la DB

    usuario_id = Column(Integer, primary_key=True, autoincrement=True)
    rol = Column(Enum(RolEnum, name="rol_enum"), nullable=False)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
