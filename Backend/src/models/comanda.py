from sqlalchemy import Boolean, Column, Date, Integer, String, Time
from sqlalchemy.orm import relationship

from src.models.base import ModeloBase


class Comanda(ModeloBase):
    __tablename__ = "comanda"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    estado = Column(String(10), nullable=False, default="abierta")  # abierta | cerrada
    activo = Column(Boolean, nullable=False, default=True)

    # FK pendiente: Mozo, Mesa, Cliente, Reserva (otros grupos)
    mozo_id = Column(Integer, nullable=False)
    mesa_id = Column(Integer, nullable=False)
    cliente_id = Column(Integer, nullable=True)
    reserva_id = Column(Integer, nullable=True)

    detalles = relationship(
        "DetalleComanda", back_populates="comanda", cascade="all, delete-orphan"
    )
    factura = relationship("Factura", back_populates="comanda", uselist=False)
