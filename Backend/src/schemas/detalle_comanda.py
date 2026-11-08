from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    @field_validator("producto_id")
    @classmethod
    def producto_no_nulo(cls, valor):
        # Omitirlo es válido (no cambia); enviarlo como null no lo es
        if valor is None:
            raise ValueError("producto_id no puede ser null")
        return valor


class DetalleComandaOut(DetalleComandaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    comanda_id: int
    entregado: bool
    activo: bool
