from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.models.base import ModeloBase


class DetalleFactura(ModeloBase):
    __tablename__ = "detalle_factura"

    id = Column(Integer, primary_key=True, index=True)
    precio_unitario = Column(Float, nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_final = Column(Float, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)

    factura_id = Column(Integer, ForeignKey("factura.id"), nullable=False)
    detalle_comanda_id = Column(Integer, ForeignKey("detalle_comanda.id"), nullable=True)
    # FK pendiente: Promocion (otro grupo)
    promocion_id = Column(Integer, nullable=True)

    factura = relationship("Factura", back_populates="detalles")
    detalle_comanda = relationship("DetalleComanda", back_populates="detalles_factura")
