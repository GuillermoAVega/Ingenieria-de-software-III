from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import ModeloBase


class MedioPago(ModeloBase):
    __tablename__ = "medio_pago"

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(100), nullable=False, unique=True)
    activo = Column(Boolean, nullable=False, default=True)

    comprobantes = relationship("ComprobantePago", back_populates="medio_pago")
