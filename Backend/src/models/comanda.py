from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Table, Time
from sqlalchemy.orm import relationship

from src.models.base import ModeloBase


comanda_mesas = Table(
    "comanda_mesas",
    ModeloBase.metadata,
    Column("comanda_id", ForeignKey("comanda.id"), primary_key=True),
    Column("mesa_id", ForeignKey("mesas.id"), primary_key=True),
)


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

    mesas_asociadas = relationship(
        "Mesa",
        secondary=comanda_mesas,
    )

    detalles = relationship(
        "DetalleComanda", back_populates="comanda", cascade="all, delete-orphan"
    )
    factura = relationship("Factura", back_populates="comanda", uselist=False)

    @property
    def mesa_ids(self) -> list[int]:
        return [mesa.id for mesa in self.mesas_asociadas]
