from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import ModeloBase


class DetalleComanda(ModeloBase):
    __tablename__ = "detalle_comanda"

    id = Column(Integer, primary_key=True, index=True)
    cantidad = Column(Integer, nullable=False)
    observaciones = Column(String(255), nullable=True)
    entregado = Column(Boolean, nullable=False, default=False)
    activo = Column(Boolean, nullable=False, default=True)

    comanda_id = Column(Integer, ForeignKey("comanda.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)

    comanda = relationship("Comanda", back_populates="detalles")
    producto = relationship("Producto")
    detalles_factura = relationship("DetalleFactura", back_populates="detalle_comanda")
