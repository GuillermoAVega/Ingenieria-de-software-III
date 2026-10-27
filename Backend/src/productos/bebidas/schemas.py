from typing import Literal

from src.productos.constants import TIPO_BEBIDA
from src.productos.schemas import ProductoBase, ProductoRespuestaBase


class BebidaCrear(ProductoBase):
    es_alcoholica: bool


class BebidaActualizar(BebidaCrear):
    # Omitido (None) conserva el estado actual
    dado_de_baja: bool | None = None


class BebidaRespuesta(ProductoRespuestaBase):
    tipo: Literal[TIPO_BEBIDA]
    es_alcoholica: bool
