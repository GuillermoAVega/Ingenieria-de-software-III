from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ComprobantePagoCreate(BaseModel):
    factura_id: int
    medio_pago_id: int
    importe: float = Field(gt=0)
    fecha_hora_emision: datetime | None = None  # por defecto: ahora


class ComprobantePagoUpdate(BaseModel):
    medio_pago_id: int | None = None
    importe: float | None = Field(default=None, gt=0)
    fecha_hora_emision: datetime | None = None


class ComprobantePagoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    factura_id: int
    medio_pago_id: int
    importe: float
    fecha_hora_emision: datetime
    activo: bool
