from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.models.base import ModeloBase


class Factura(ModeloBase):
    __tablename__ = "factura"

    id = Column(Integer, primary_key=True, index=True)
    importe_total = Column(Float, nullable=False, default=0)
    fecha_hora_emision = Column(DateTime, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)

    comanda_id = Column(Integer, ForeignKey("comanda.id"), nullable=False, index=True)

    comanda = relationship("Comanda", back_populates="factura")
    detalles = relationship(
        "DetalleFactura", back_populates="factura", cascade="all, delete-orphan"
    )
    comprobantes = relationship("ComprobantePago", back_populates="factura")
