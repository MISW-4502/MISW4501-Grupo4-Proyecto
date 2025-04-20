from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class Pedido(Base):
    __tablename__ = 'pedido'

    pedido_id = Column(Integer, primary_key=True)
    id_cliente = Column(Integer, nullable=False)
    id_vendedor = Column(Integer, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)
    estado = Column(String(50), default='PENDIENTE')
    total = Column(Numeric(14, 2), default=0)

    detalles = relationship("DetallePedido", back_populates="pedido", cascade="all, delete-orphan")

class DetallePedido(Base):
    __tablename__ = 'detalle_pedido'

    detalle_id = Column(Integer, primary_key=True)
    id_pedido = Column(Integer, ForeignKey('pedido.pedido_id', ondelete='CASCADE'))
    id_producto = Column(Integer, nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    subtotal = Column(Numeric(14, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="detalles")

class EstadoPedidoEnum(enum.Enum):
    PENDIENTE = "PENDIENTE"
    EN_REVISION = "EN_REVISION"
    ENVIADO = "ENVIADO"
    ENTREGADO = "ENTREGADO"
    FACTURADO = "FACTURADO"
    CANCELADO = "CANCELADO"
