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

    # Un mozo puede tener varias comandas; las comandas de reserva no tienen mozo
    mozo_id = Column(Integer, ForeignKey("mozos.id"), nullable=True)
    mesa_id = Column(Integer, ForeignKey("mesas.id"), nullable=False)
    cliente_id = Column(Integer, nullable=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=True)

    mozo = relationship("Mozo", back_populates="comandas")
    mesa = relationship(
        "Mesa",
        foreign_keys=[mesa_id],
        back_populates="comandas",
    )
    reserva = relationship("Reserva", back_populates="comanda")

    mesas_asociadas = relationship(
        "Mesa",
        secondary=comanda_mesas,
        back_populates="comandas_asociadas",
    )

    detalles = relationship(
        "DetalleComanda", back_populates="comanda", cascade="all, delete-orphan"
    )
    factura = relationship("Factura", back_populates="comanda", uselist=False)

    @property
    def mesa_ids(self) -> list[int]:
        return [mesa.id for mesa in self.mesas_asociadas]
