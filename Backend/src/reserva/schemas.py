from datetime import date, time

from pydantic import BaseModel, Field

from src.detalleReserva.schemas import DetalleReserva, DetalleReservaCreate
from src.reserva.estados import EstadoReserva


class ReservaBase(BaseModel):
    fecha: date
    hora: time
    cant_comensales: int
    observaciones: str | None = None
    cliente_id: int


class ReservaCreate(ReservaBase):
    mesa_ids: list[int] = Field(default_factory=list)
    detalles: list[DetalleReservaCreate] = Field(default_factory=list)


class ReservaUpdate(ReservaBase):
    estado: EstadoReserva


class Reserva(ReservaBase):
    id: int
    estado: EstadoReserva
    mesa_ids: list[int]
    detalles: list[DetalleReserva]

    model_config = {
        "from_attributes": True
    }


class ReservaMesaCreate(BaseModel):
    mesa_id: int
