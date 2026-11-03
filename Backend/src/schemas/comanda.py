from datetime import date, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.schemas.detalle_comanda import DetalleComandaNested, DetalleComandaOut


class ComandaCreate(BaseModel):
    fecha: date | None = None
    hora: time | None = None
    mozo_id: int | None = None
    mesa_id: int | None = None
    mesa_ids: list[int] | None = Field(default=None, min_length=1)
    comensales: int | None = Field(default=None, gt=0)
    cliente_id: int | None = None
    reserva_id: int | None = None
    detalles: list[DetalleComandaNested] = []

    @model_validator(mode="after")
    def validar_mozo_segun_reserva(self):
        if self.reserva_id is not None and self.mozo_id is not None:
            raise ValueError("Una comanda con reserva no puede tener mozo asignado")
        return self


class ComandaUpdate(BaseModel):
    fecha: date | None = None
    hora: time | None = None
    mozo_id: int | None = None
    mesa_id: int | None = None
    mesa_ids: list[int] | None = Field(default=None, min_length=1)
    cliente_id: int | None = None
    reserva_id: int | None = None
    estado: Literal["abierta", "cerrada"] | None = None


class ComandaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha: date
    hora: time
    mozo_id: int | None
    mesa_id: int | None
    mesa_ids: list[int] = []
    cliente_id: int | None
    reserva_id: int | None
    estado: str
    activo: bool
    detalles: list[DetalleComandaOut] = []

    @field_validator("detalles")
    @classmethod
    def solo_activos(cls, detalles):
        return [d for d in detalles if d.activo]
