from __future__ import annotations

from datetime import date, time

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import ModeloBase


class Reserva(ModeloBase):
    __tablename__ = "reservas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    hora: Mapped[time] = mapped_column(Time, nullable=False)
    cant_comensales: Mapped[int] = mapped_column(Integer, nullable=False)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    cliente_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("clientes.id"),
        nullable=False,
    )
    estado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    detalles: Mapped[list[DetalleReserva]] = relationship(
        back_populates="reserva",
        cascade="all, delete-orphan",
    )
    mesas_asociadas: Mapped[list[ReservaMesa]] = relationship(
        back_populates="reserva",
        cascade="all, delete-orphan",
    )

    @property
    def mesa_ids(self) -> list[int]:
        return [asociacion.mesa_id for asociacion in self.mesas_asociadas]


class ReservaMesa(ModeloBase):
    __tablename__ = "reserva_mesas"

    reserva_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reservas.id"),
        primary_key=True,
    )
    mesa_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mesas.id"),
        primary_key=True,
    )

    reserva: Mapped[Reserva] = relationship(back_populates="mesas_asociadas")