from typing import Literal

from pydantic import Field

from src.productos.constants import TIPO_PLATO
from src.productos.platos.constants import CANT_PERSONAS_MIN
from src.productos.schemas import ProductoBase, ProductoRespuestaBase


class PlatoCrear(ProductoBase):
    cant_personas: int = Field(ge=CANT_PERSONAS_MIN)


class PlatoActualizar(PlatoCrear):
    # Omitido (None) conserva el estado actual
    dado_de_baja: bool | None = None


class PlatoRespuesta(ProductoRespuestaBase):
    tipo: Literal[TIPO_PLATO]
    cant_personas: int
