import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer

Base = declarative_base()

class Truck(Base):
    __tablename__ = 'trucks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    license_plate = Column(String(20), nullable=False, unique=True)
    model = Column(String(50), nullable=False)
    brand = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default='ACTIVE')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
