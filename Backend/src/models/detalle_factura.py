from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.models.base import ModeloBase


class DetalleFactura(ModeloBase):
    __tablename__ = "detalle_factura"

    id = Column(Integer, primary_key=True, index=True)
    precio_unitario = Column(Float, nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_final = Column(Float, nullable=False)
    # Calculadas por el motor de promociones (lleva_paga); 0 sin bonificación
    unidades_gratis = Column(Integer, nullable=False, default=0, server_default="0")
    activo = Column(Boolean, nullable=False, default=True)

    factura_id = Column(Integer, ForeignKey("factura.id"), nullable=False)
    detalle_comanda_id = Column(Integer, ForeignKey("detalle_comanda.id"), nullable=False)
    promocion_id = Column(Integer, ForeignKey("promocion.id"), nullable=True)

    factura = relationship("Factura", back_populates="detalles")
    detalle_comanda = relationship("DetalleComanda", back_populates="detalles_factura")
    # Referencia a Promocion solo por cadena (`main` carga su modelo)
    promocion = relationship("Promocion")
