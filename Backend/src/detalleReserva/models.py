from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import ModeloBase
from src.reserva.models import Reserva

if TYPE_CHECKING:
    from src.productos.models import Producto


class DetalleReserva(ModeloBase):
    __tablename__ = "detalle_reserva"

    reserva_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reservas.id"),
        primary_key=True,
    )
    producto_id: Mapped[int] = mapped_column(
        ForeignKey("producto.id"),
        primary_key=True,
    )
    cantidad_producto: Mapped[int] = mapped_column(Integer, nullable=False)

    reserva: Mapped[Reserva] = relationship(back_populates="detalles")
    producto: Mapped["Producto"] = relationship(back_populates="detalles_reserva")
