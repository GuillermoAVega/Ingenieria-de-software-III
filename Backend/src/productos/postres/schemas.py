from typing import Literal

from src.productos.constants import TIPO_POSTRE
from src.productos.schemas import ProductoBase, ProductoRespuestaBase


class PostreCrear(ProductoBase):
    pass


class PostreActualizar(PostreCrear):
    # Omitido (None) conserva el estado actual
    dado_de_baja: bool | None = None


class PostreRespuesta(ProductoRespuestaBase):
    tipo: Literal[TIPO_POSTRE]
