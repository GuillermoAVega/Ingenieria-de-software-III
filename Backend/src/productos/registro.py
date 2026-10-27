# Único módulo que conoce todos los subpaquetes: al importarlo quedan cargados
# los cinco modelos y los mappers pueden resolver las relaciones por cadena
from typing import Annotated, Union

from pydantic import Field

from src.productos.bebidas.models import Bebida
from src.productos.bebidas.schemas import BebidaRespuesta
from src.productos.combos.models import (
    ComboPromocion,
    combo_bebida,
    combo_plato,
    combo_postre,
)
from src.productos.combos.schemas import ComboRespuesta
from src.productos.constants import (
    TIPO_BEBIDA,
    TIPO_COMBO_PROMOCION,
    TIPO_MENU_EJECUTIVO,
    TIPO_PLATO,
    TIPO_POSTRE,
)
from src.productos.menus_ejecutivos.models import MenuEjecutivo
from src.productos.menus_ejecutivos.schemas import MenuRespuesta
from src.productos.platos.models import Plato
from src.productos.platos.schemas import PlatoRespuesta
from src.productos.postres.models import Postre
from src.productos.postres.schemas import PostreRespuesta

# Clase concreta de cada valor del discriminador `tipo`
MODELOS_POR_TIPO = {
    TIPO_PLATO: Plato,
    TIPO_BEBIDA: Bebida,
    TIPO_POSTRE: Postre,
    TIPO_MENU_EJECUTIVO: MenuEjecutivo,
    TIPO_COMBO_PROMOCION: ComboPromocion,
}

# Respuesta polimórfica: `tipo` decide el esquema. Vive aquí (y no en
# productos/schemas.py) para evitar el ciclo productos.schemas <-> <sub>.schemas
ProductoRespuesta = Annotated[
    Union[
        PlatoRespuesta,
        BebidaRespuesta,
        PostreRespuesta,
        MenuRespuesta,
        ComboRespuesta,
    ],
    Field(discriminator="tipo"),
]

__all__ = [
    "ProductoRespuesta",
    "MODELOS_POR_TIPO",
    "Bebida",
    "ComboPromocion",
    "MenuEjecutivo",
    "Plato",
    "Postre",
    "combo_bebida",
    "combo_plato",
    "combo_postre",
]
