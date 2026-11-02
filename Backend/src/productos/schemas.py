from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.productos.constants import (
    DESCRIPCION_MAX,
    NOMBRE_MAX,
    PRECIO_DECIMALES,
    PRECIO_DIGITOS,
)

Precio = Annotated[
    Decimal,
    Field(gt=0, max_digits=PRECIO_DIGITOS, decimal_places=PRECIO_DECIMALES),
]


class ProductoBase(BaseModel):
    """Campos comunes a todos los productos."""
    nombre: str = Field(min_length=1, max_length=NOMBRE_MAX)
    precio: Precio
    descripcion: str | None = Field(default=None, max_length=DESCRIPCION_MAX)
    imagen: str | None = None
    seccion_id: int | None = None

    # Se recorta antes de validar la longitud: vacío o solo espacios queda rechazado
    @field_validator("nombre", mode="before")
    @classmethod
    def recortar_nombre(cls, valor):
        return valor.strip() if isinstance(valor, str) else valor


class ProductoRespuestaBase(BaseModel):
    """Campos comunes de toda respuesta; se construye desde el modelo ORM."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    precio: Decimal
    descripcion: str | None
    imagen: str | None
    dado_de_baja: bool
    seccion_id: int | None
