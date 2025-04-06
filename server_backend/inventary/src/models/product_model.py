import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, Numeric

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    manufacturer = Column(String(255), nullable=True)  # Nuevo campo
    location = Column(String(255), nullable=True)      # Nuevo campo
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
