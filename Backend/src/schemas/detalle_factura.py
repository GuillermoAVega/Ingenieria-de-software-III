from pydantic import BaseModel, ConfigDict, Field, field_validator


# Los precios y la promoción los calcula el servidor: si el cliente envía
# `precio_unitario`, `precio_final`, `promocion_id` o `unidades_gratis`, Pydantic los ignora.
class DetalleFacturaCreate(BaseModel):
    factura_id: int
    detalle_comanda_id: int
    cantidad: int = Field(gt=0)


class DetalleFacturaUpdate(BaseModel):
    detalle_comanda_id: int | None = None
    cantidad: int | None = Field(default=None, gt=0)

    @field_validator("detalle_comanda_id", "cantidad")
    @classmethod
    def no_nulo(cls, valor):
        # Omitirlos es válido (no cambian); enviarlos como null no lo es
        if valor is None:
            raise ValueError("no puede ser null")
        return valor


class DetalleFacturaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    factura_id: int
    detalle_comanda_id: int
    promocion_id: int | None
    precio_unitario: float
    cantidad: int
    precio_final: float
    unidades_gratis: int
    activo: bool
