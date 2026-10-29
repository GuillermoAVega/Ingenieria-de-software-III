from datetime import date
from pydantic import BaseModel, field_validator
from typing import Optional


class AtencionBase(BaseModel):
    fecha_desde: date
    fecha_hasta: Optional[date] = None
    mozo_id: int
    sector_id: int

    @field_validator("fecha_hasta")
    @classmethod
    def validar_fecha_hasta(cls, v: Optional[date], info) -> Optional[date]:
        fecha_desde = info.data.get("fecha_desde")
        if v is not None and fecha_desde is not None and v < fecha_desde:
            raise ValueError("fecha_hasta debe ser mayor o igual a fecha_desde")
        return v


class AtencionCreate(BaseModel):
    fecha_desde: date
    mozo_id: int
    sector_id: int

    @field_validator("fecha_desde")
    @classmethod
    def validar_fecha_desde(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("fecha_desde no puede ser posterior a hoy")
        return v


class AtencionUpdate(BaseModel):
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None

    @field_validator("fecha_desde", "fecha_hasta")
    @classmethod
    def validar_fecha_no_futura(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("Las fechas de atención no pueden ser posteriores a hoy")
        return v


class Atencion(AtencionBase):
    id: int
    estado: bool

    model_config = {"from_attributes": True}
