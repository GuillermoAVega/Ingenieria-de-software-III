from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FacturaCreate(BaseModel):
    comanda_id: int
    fecha_hora_emision: datetime | None = None  # por defecto: ahora


class FacturaUpdate(BaseModel):
    fecha_hora_emision: datetime | None = None


class FacturaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    comanda_id: int
    importe_total: float
    fecha_hora_emision: datetime
    activo: bool
