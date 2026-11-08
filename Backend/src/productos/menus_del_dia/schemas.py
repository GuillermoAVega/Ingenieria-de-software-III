from datetime import date
from typing import Literal

from src.productos.constants import TIPO_MENU_DEL_DIA
from src.productos.schemas import ProductoBase, ProductoRespuestaBase


class MenuDelDiaCrear(ProductoBase):
    pass


class MenuDelDiaActualizar(MenuDelDiaCrear):
    # Omitido (None) conserva el estado actual
    dado_de_baja: bool | None = None


class MenuDelDiaRespuesta(ProductoRespuestaBase):
    tipo: Literal[TIPO_MENU_DEL_DIA]


class MenuDelDiaListado(MenuDelDiaRespuesta):
    # Fecha asignada más cercana desde hoy (inclusive); None si no tiene ninguna
    proxima_fecha: date | None = None
