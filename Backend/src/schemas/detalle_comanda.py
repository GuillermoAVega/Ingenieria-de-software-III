from pydantic import BaseModel, ConfigDict, Field


class DetalleComandaBase(BaseModel):
    cantidad: int = Field(gt=0)
    observaciones: str | None = Field(default=None, max_length=255)
    producto_id: int


class DetalleComandaNested(DetalleComandaBase):
    """Detalle enviado dentro de la creación de una comanda."""


class DetalleComandaCreate(DetalleComandaBase):
    comanda_id: int


class DetalleComandaUpdate(BaseModel):
    cantidad: int | None = Field(default=None, gt=0)
    observaciones: str | None = Field(default=None, max_length=255)
    producto_id: int | None = None
    entregado: bool | None = None


class DetalleComandaOut(DetalleComandaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    comanda_id: int
    entregado: bool
    activo: bool
