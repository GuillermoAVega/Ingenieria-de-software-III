from pydantic import BaseModel, ConfigDict, Field


class DetalleFacturaCreate(BaseModel):
    factura_id: int
    detalle_comanda_id: int | None = None
    promocion_id: int | None = None
    precio_unitario: float = Field(ge=0)
    cantidad: int = Field(gt=0)
    precio_final: float | None = Field(default=None, ge=0)  # por defecto: unitario * cantidad


class DetalleFacturaUpdate(BaseModel):
    detalle_comanda_id: int | None = None
    promocion_id: int | None = None
    precio_unitario: float | None = Field(default=None, ge=0)
    cantidad: int | None = Field(default=None, gt=0)
    precio_final: float | None = Field(default=None, ge=0)


class DetalleFacturaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    factura_id: int
    detalle_comanda_id: int | None
    promocion_id: int | None
    precio_unitario: float
    cantidad: int
    precio_final: float
    activo: bool
