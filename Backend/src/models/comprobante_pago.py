from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.models.base import ModeloBase


class ComprobantePago(ModeloBase):
    __tablename__ = "comprobante_pago"

    id = Column(Integer, primary_key=True, index=True)
    importe = Column(Float, nullable=False)
    fecha_hora_emision = Column(DateTime, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)

    factura_id = Column(Integer, ForeignKey("factura.id"), nullable=False)
    medio_pago_id = Column(Integer, ForeignKey("medio_pago.id"), nullable=False)

    factura = relationship("Factura", back_populates="comprobantes")
    medio_pago = relationship("MedioPago", back_populates="comprobantes")
