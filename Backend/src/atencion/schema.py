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


class AtencionUpdate(BaseModel):
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None


class Atencion(AtencionBase):
    id: int
    estado: bool

    model_config = {"from_attributes": True}
