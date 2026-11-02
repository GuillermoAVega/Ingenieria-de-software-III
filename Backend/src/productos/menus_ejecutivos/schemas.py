from typing import Literal

from src.productos.constants import TIPO_MENU_EJECUTIVO
from src.productos.schemas import ProductoBase, ProductoRespuestaBase


class MenuCrear(ProductoBase):
    plato_id: int
    postre_id: int


class MenuActualizar(MenuCrear):
    # Omitido (None) conserva el estado actual
    dado_de_baja: bool | None = None


class MenuRespuesta(ProductoRespuestaBase):
    tipo: Literal[TIPO_MENU_EJECUTIVO]
    plato_id: int
    postre_id: int
