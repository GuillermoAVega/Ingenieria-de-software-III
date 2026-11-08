from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator, model_validator

from src.promociones.constants import DESCUENTO_DECIMALES, DESCUENTO_MAXIMO, NOMBRE_MAX


class PromocionCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=NOMBRE_MAX)
    tipo: Literal["porcentaje", "lleva_paga"]
    fecha_desde: date
    fecha_hasta: date
    # `null` equivale a ausente; la obligatoriedad depende del tipo
    descuento: Decimal | None = Field(
        default=None, gt=0, le=DESCUENTO_MAXIMO, decimal_places=DESCUENTO_DECIMALES
    )
    lleva: StrictInt | None = None
    paga: StrictInt | None = None
    productos_ids: list[int] = Field(min_length=1)

    # Se recorta antes de validar la longitud: vacío o solo espacios queda rechazado
    @field_validator("nombre", mode="before")
    @classmethod
    def recortar_nombre(cls, valor):
        return valor.strip() if isinstance(valor, str) else valor

    @field_validator("productos_ids")
    @classmethod
    def sin_duplicados(cls, ids):
        if len(ids) != len(set(ids)):
            raise ValueError("Los ids de productos no pueden repetirse")
        return ids

    @model_validator(mode="after")
    def validar_rango_de_fechas(self):
        if self.fecha_desde > self.fecha_hasta:
            raise ValueError("fecha_desde no puede ser posterior a fecha_hasta")
        return self


    @model_validator(mode="after")
    def validar_parametros_del_tipo(self):
        if self.tipo == "porcentaje":
            if self.descuento is None:
                raise ValueError("El tipo porcentaje requiere descuento")
            if self.lleva is not None or self.paga is not None:
                raise ValueError("El tipo porcentaje no admite lleva ni paga")
        else:
            if self.descuento is not None:
                raise ValueError("El tipo lleva_paga no admite descuento")
            if self.lleva is None or self.paga is None:
                raise ValueError("El tipo lleva_paga requiere lleva y paga")
            if self.paga < 1 or self.lleva <= self.paga:
                raise ValueError("Se requiere lleva > paga >= 1")
        return self


# El PUT es un reemplazo completo con las mismas reglas del alta
PromocionActualizar = PromocionCrear


class PromocionRespuesta(BaseModel):
    """Respuesta de una promoción; se construye desde el modelo ORM."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    tipo: str
    fecha_desde: date
    fecha_hasta: date
    descuento: Decimal | None
    lleva: int | None
    paga: int | None
    dado_de_baja: bool
    productos_ids: list[int]
    # True si algún detalle_factura (activo o no) la referencia; no es columna
    en_uso: bool = False
